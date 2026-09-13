from collections import OrderedDict
from threading import Lock
from typing import Annotated

from fastapi import Depends, Request

from app.modules.cnc.services.machining_report import MachiningReportSource


class MachiningReportStore:
    """Bounded process-local snapshots, never an authority or durable CNC archive."""

    def __init__(self) -> None:
        self._sources: OrderedDict[tuple[str, str], MachiningReportSource] = OrderedDict()
        self._lock = Lock()

    def save(self, plan_id: str, source: MachiningReportSource) -> None:
        key = (source.owner_user_id, plan_id)
        with self._lock:
            self._sources[key] = source
            self._sources.move_to_end(key)
            while len(self._sources) > 256:
                self._sources.popitem(last=False)

    def get_owned(self, plan_id: str, owner_user_id: str) -> MachiningReportSource | None:
        with self._lock:
            return self._sources.get((owner_user_id, plan_id))


def get_machining_report_store(request: Request) -> MachiningReportStore:
    return request.app.state.machining_report_store


MachiningReportStoreDependency = Annotated[
    MachiningReportStore, Depends(get_machining_report_store)
]
