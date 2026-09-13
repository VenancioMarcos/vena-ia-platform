from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Request

from app.modules.cam.schemas import (
    TurningBoundingBox,
    TurningPlanGatewayRequest,
    TurningPlanGatewayResponse,
)


class TurningPlanNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class TurningPlanRecord:
    owner_user_id: str
    request: TurningPlanGatewayRequest
    response: TurningPlanGatewayResponse
    source_brep_bounds: TurningBoundingBox


class TurningPlanStore:
    """Process-local, owner-scoped handoff from CAM planning to CNC review output."""

    def __init__(self) -> None:
        self._records: dict[str, TurningPlanRecord] = {}

    def save(
        self,
        *,
        owner_user_id: str,
        request: TurningPlanGatewayRequest,
        response: TurningPlanGatewayResponse,
        source_brep_bounds: TurningBoundingBox,
    ) -> None:
        self._records[response.plan_id] = TurningPlanRecord(
            owner_user_id=owner_user_id,
            request=request,
            response=response,
            source_brep_bounds=source_brep_bounds,
        )

    def get_owned(self, plan_id: str, *, owner_user_id: str) -> TurningPlanRecord:
        record = self._records.get(plan_id)
        if record is None or record.owner_user_id != owner_user_id:
            raise TurningPlanNotFoundError("turning plan not found")
        return record


def get_turning_plan_store(request: Request) -> TurningPlanStore:
    return request.app.state.turning_plan_store


TurningPlanStoreDependency = Annotated[TurningPlanStore, Depends(get_turning_plan_store)]
