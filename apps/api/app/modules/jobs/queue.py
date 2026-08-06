from __future__ import annotations

import json
import hashlib
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import asdict
from typing import Any, Protocol, cast

from redis import Redis
from redis.exceptions import RedisError

from app.modules.jobs.contracts import ClaimedJob, JobQueueMessage


class JobQueueUnavailable(RuntimeError):
    pass


class InvalidJobQueueMessage(JobQueueUnavailable):
    def __init__(self, job_id: str) -> None:
        super().__init__("Invalid asynchronous queue message")
        self.job_id = job_id


class JobQueue(Protocol):
    def enqueue(self, message: JobQueueMessage, delay_seconds: float = 0) -> bool: ...
    def claim(self, worker_id: str, lease_seconds: int) -> ClaimedJob | None: ...
    def acknowledge(self, job_id: str, worker_id: str) -> None: ...
    def retry(self, message: JobQueueMessage, worker_id: str, delay_seconds: float) -> None: ...
    def recover_abandoned(self) -> list[str]: ...
    def extend_lease(self, job_id: str, worker_id: str, lease_seconds: int) -> None: ...
    def has_active_lease(self, job_id: str) -> bool: ...
    def ping(self) -> bool: ...
    def heartbeat(self, worker_id: str, ttl_seconds: int) -> None: ...
    def worker_available(self) -> bool: ...


class MemoryJobQueue:
    """Deterministic test queue; intentionally forbidden in production."""

    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self._clock = clock
        self._ready: deque[str] = deque()
        self._messages: dict[str, JobQueueMessage] = {}
        self._delayed: dict[str, float] = {}
        self._leases: dict[str, tuple[str, float]] = {}
        self._lock = threading.Lock()
        self._heartbeat_until = 0.0

    def enqueue(self, message: JobQueueMessage, delay_seconds: float = 0) -> bool:
        with self._lock:
            self._messages[message.job_id] = message
            if (
                message.job_id in self._ready
                or message.job_id in self._delayed
                or message.job_id in self._leases
            ):
                return False
            if delay_seconds > 0:
                self._delayed[message.job_id] = self._clock() + delay_seconds
            elif message.job_id not in self._ready and message.job_id not in self._leases:
                self._ready.append(message.job_id)
            return True

    def _promote(self) -> None:
        now = self._clock()
        due = [job_id for job_id, at in self._delayed.items() if at <= now]
        for job_id in due:
            del self._delayed[job_id]
            if job_id not in self._leases:
                self._ready.append(job_id)

    def claim(self, worker_id: str, lease_seconds: int) -> ClaimedJob | None:
        with self._lock:
            self._promote()
            while self._ready:
                job_id = self._ready.popleft()
                if job_id in self._leases:
                    continue
                message = self._messages.get(job_id)
                if message is None:
                    continue
                self._leases[job_id] = (worker_id, self._clock() + lease_seconds)
                return ClaimedJob(message, worker_id)
        return None

    def acknowledge(self, job_id: str, worker_id: str) -> None:
        with self._lock:
            lease = self._leases.get(job_id)
            if lease is None and job_id not in self._messages:
                return
            if lease is None or lease[0] != worker_id:
                raise JobQueueUnavailable("Job lease ownership mismatch")
            del self._leases[job_id]
            self._messages.pop(job_id, None)
            self._delayed.pop(job_id, None)

    def retry(self, message: JobQueueMessage, worker_id: str, delay_seconds: float) -> None:
        with self._lock:
            lease = self._leases.get(message.job_id)
            if lease is None or lease[0] != worker_id:
                raise JobQueueUnavailable("Job lease ownership mismatch")
            del self._leases[message.job_id]
            self._messages[message.job_id] = message
            self._delayed[message.job_id] = self._clock() + max(delay_seconds, 0)

    def recover_abandoned(self) -> list[str]:
        with self._lock:
            now = self._clock()
            expired = [job_id for job_id, (_, until) in self._leases.items() if until <= now]
            for job_id in expired:
                del self._leases[job_id]
                if job_id in self._messages:
                    self._ready.appendleft(job_id)
            return expired

    def extend_lease(self, job_id: str, worker_id: str, lease_seconds: int) -> None:
        with self._lock:
            lease = self._leases.get(job_id)
            if lease is None or lease[0] != worker_id:
                raise JobQueueUnavailable("Job lease ownership mismatch")
            self._leases[job_id] = (worker_id, self._clock() + lease_seconds)

    def has_active_lease(self, job_id: str) -> bool:
        with self._lock:
            lease = self._leases.get(job_id)
            return bool(lease and lease[1] > self._clock())

    def ping(self) -> bool:
        return True

    def heartbeat(self, worker_id: str, ttl_seconds: int) -> None:
        del worker_id
        self._heartbeat_until = self._clock() + ttl_seconds

    def worker_available(self) -> bool:
        return self._heartbeat_until > self._clock()


class RedisJobQueue:
    """Redis-backed queue with atomic claim and expiring visibility leases."""

    _CLAIM = """
    local delayed = redis.call('ZRANGEBYSCORE', KEYS[2], '-inf', ARGV[1])
    for _, id in ipairs(delayed) do
      redis.call('ZREM', KEYS[2], id)
      redis.call('RPUSH', KEYS[1], id)
    end
    for i=1,100 do
      local id = redis.call('LPOP', KEYS[1])
      if not id then return nil end
      if redis.call('ZADD', KEYS[3], 'NX', ARGV[2], id) == 1 then
        redis.call('HSET', KEYS[4], id, ARGV[3])
        local payload = redis.call('HGET', KEYS[5], id)
        if payload then return {id, payload} end
        redis.call('ZREM', KEYS[3], id)
        redis.call('HDEL', KEYS[4], id)
      end
    end
    return nil
    """

    _ACK = """
    local owner = redis.call('HGET', KEYS[2], ARGV[1])
    if not owner and redis.call('HEXISTS', KEYS[3], ARGV[1]) == 0 then return 2 end
    if owner ~= ARGV[2] then return 0 end
    redis.call('ZREM', KEYS[1], ARGV[1])
    redis.call('HDEL', KEYS[2], ARGV[1])
    redis.call('HDEL', KEYS[3], ARGV[1])
    redis.call('SREM', KEYS[4], ARGV[1])
    return 1
    """

    _ENQUEUE = """
    redis.call('HSET', KEYS[1], ARGV[1], ARGV[2])
    if redis.call('SADD', KEYS[4], ARGV[1]) == 0 then return 0 end
    if tonumber(ARGV[3]) > 0 then
      redis.call('ZADD', KEYS[3], ARGV[4], ARGV[1])
    else
      redis.call('RPUSH', KEYS[2], ARGV[1])
    end
    return 1
    """

    _RECOVER = """
    local expired = redis.call('ZRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
    local recovered = {}
    for _, id in ipairs(expired) do
      if redis.call('ZREM', KEYS[1], id) == 1 then
        redis.call('HDEL', KEYS[2], id)
        if redis.call('HEXISTS', KEYS[4], id) == 1 then
          redis.call('SADD', KEYS[5], id)
          redis.call('LPUSH', KEYS[3], id)
          table.insert(recovered, id)
        end
      end
    end
    return recovered
    """

    _EXTEND = """
    if redis.call('HGET', KEYS[2], ARGV[1]) ~= ARGV[2] then return 0 end
    redis.call('ZADD', KEYS[1], 'XX', ARGV[3], ARGV[1])
    return 1
    """

    def __init__(self, client: Redis, prefix: str) -> None:
        self._client = client
        self._prefix = prefix.rstrip(":")

    def _key(self, suffix: str) -> str:
        return f"{self._prefix}:{suffix}"

    @staticmethod
    def _payload(message: JobQueueMessage) -> str:
        return json.dumps(asdict(message), separators=(",", ":"), sort_keys=True)

    def enqueue(self, message: JobQueueMessage, delay_seconds: float = 0) -> bool:
        try:
            result = self._client.eval(
                self._ENQUEUE,
                4,
                self._key("payloads"),
                self._key("ready"),
                self._key("delayed"),
                self._key("scheduled"),
                message.job_id,
                self._payload(message),
                str(max(delay_seconds, 0)),
                str(time.time() + max(delay_seconds, 0)),
            )
            return result == 1
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc

    def claim(self, worker_id: str, lease_seconds: int) -> ClaimedJob | None:
        now = time.time()
        try:
            raw = cast(
                Any,
                self._client.eval(
                    self._CLAIM,
                    5,
                    self._key("ready"),
                    self._key("delayed"),
                    self._key("leases"),
                    self._key("workers"),
                    self._key("payloads"),
                    str(now),
                    str(now + lease_seconds),
                    worker_id,
                ),
            )
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc
        if raw is None:
            return None
        job_id = raw[0].decode() if isinstance(raw[0], bytes) else str(raw[0])
        try:
            payload = json.loads(raw[1])
            message = JobQueueMessage(**payload)
            if message.job_id != job_id:
                raise ValueError("Queue identifier mismatch")
        except (json.JSONDecodeError, TypeError, ValueError):
            self.acknowledge(job_id, worker_id)
            raise InvalidJobQueueMessage(job_id) from None
        return ClaimedJob(message, worker_id)

    def acknowledge(self, job_id: str, worker_id: str) -> None:
        try:
            result = self._client.eval(
                self._ACK,
                4,
                self._key("leases"),
                self._key("workers"),
                self._key("payloads"),
                self._key("scheduled"),
                job_id,
                worker_id,
            )
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc
        if result not in {1, 2}:
            raise JobQueueUnavailable("Job lease ownership mismatch")

    def retry(self, message: JobQueueMessage, worker_id: str, delay_seconds: float) -> None:
        try:
            with self._client.pipeline(transaction=True) as pipe:
                pipe.watch(self._key("workers"))
                owner = pipe.hget(self._key("workers"), message.job_id)
                if owner != worker_id and owner != worker_id.encode():
                    pipe.unwatch()
                    raise JobQueueUnavailable("Job lease ownership mismatch")
                pipe.multi()
                pipe.zrem(self._key("leases"), message.job_id)
                pipe.hdel(self._key("workers"), message.job_id)
                pipe.hset(self._key("payloads"), message.job_id, self._payload(message))
                pipe.sadd(self._key("scheduled"), message.job_id)
                pipe.zadd(
                    self._key("delayed"),
                    {message.job_id: time.time() + max(delay_seconds, 0)},
                )
                pipe.execute()
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc

    def recover_abandoned(self) -> list[str]:
        try:
            raw_ids = cast(
                list[str | bytes],
                self._client.eval(
                    self._RECOVER,
                    5,
                    self._key("leases"),
                    self._key("workers"),
                    self._key("ready"),
                    self._key("payloads"),
                    self._key("scheduled"),
                    str(time.time()),
                ),
            )
            return [raw.decode() if isinstance(raw, bytes) else raw for raw in raw_ids]
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc

    def extend_lease(self, job_id: str, worker_id: str, lease_seconds: int) -> None:
        try:
            result = self._client.eval(
                self._EXTEND,
                2,
                self._key("leases"),
                self._key("workers"),
                job_id,
                worker_id,
                str(time.time() + lease_seconds),
            )
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc
        if result != 1:
            raise JobQueueUnavailable("Job lease ownership mismatch")

    def has_active_lease(self, job_id: str) -> bool:
        try:
            score = cast(Any, self._client.zscore(self._key("leases"), job_id))
            return score is not None and float(score) > time.time()
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc

    def ping(self) -> bool:
        try:
            return bool(self._client.ping())
        except RedisError:
            return False

    def heartbeat(self, worker_id: str, ttl_seconds: int) -> None:
        try:
            identity = hashlib.sha256(worker_id.encode()).hexdigest()[:16]
            self._client.set(self._key(f"worker:heartbeat:{identity}"), "alive", ex=ttl_seconds)
        except RedisError as exc:
            raise JobQueueUnavailable("Asynchronous queue is unavailable") from exc

    def worker_available(self) -> bool:
        try:
            return any(self._client.scan_iter(match=self._key("worker:heartbeat:*"), count=10))
        except RedisError:
            return False
