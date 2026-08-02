import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts.backup_contract import BackupContractError
from scripts.backup_job import ExclusiveBackupLock, run_scheduled_worker


def test_exclusive_lock_refuses_concurrent_job_and_cleans_after_exit(tmp_path: Path) -> None:
    lock_path = tmp_path / ".backup.lock"
    with ExclusiveBackupLock(lock_path):
        assert lock_path.is_file()
        with pytest.raises(BackupContractError, match="already holds"):
            with ExclusiveBackupLock(lock_path):
                pass
    assert not lock_path.exists()


def test_scheduled_worker_uses_internal_command_and_predictable_success(tmp_path: Path) -> None:
    calls: list[tuple[list[str], dict[str, Any]]] = []

    def runner(command: list[str], **kwargs: Any) -> None:
        calls.append((command, kwargs))

    lock = tmp_path / ".backup.lock"
    run_scheduled_worker(lock, 30, runner=runner)
    assert calls[0][0][-3:] == ["-m", "scripts.backup_job", "--worker"]
    assert calls[0][1]["timeout"] == 30
    assert calls[0][1]["check"] is True
    assert not lock.exists()


def test_timeout_and_worker_failure_release_lock(tmp_path: Path) -> None:
    lock = tmp_path / ".backup.lock"

    def timeout_runner(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise subprocess.TimeoutExpired("backup", 1)

    with pytest.raises(BackupContractError, match="timeout"):
        run_scheduled_worker(lock, 1, runner=timeout_runner)
    assert not lock.exists()

    def failing_runner(*args: Any, **kwargs: Any) -> None:
        del args, kwargs
        raise subprocess.CalledProcessError(2, "backup")

    with pytest.raises(BackupContractError, match="failed"):
        run_scheduled_worker(lock, 1, runner=failing_runner)
    assert not lock.exists()


def test_invalid_timeout_fails_before_lock(tmp_path: Path) -> None:
    lock = tmp_path / ".backup.lock"
    with pytest.raises(BackupContractError, match="positive"):
        run_scheduled_worker(lock, 0)
    assert not lock.exists()
