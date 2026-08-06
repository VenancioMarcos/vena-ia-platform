from fastapi import HTTPException

from app.modules.engineering.models import EngineeringCatalogItem
from app.modules.engineering.repository import EngineeringCatalogRepository
from app.modules.engineering.schemas import (
    CatalogItemCreate,
    CatalogItemRead,
    CatalogKind,
    PreliminarySelection,
    SelectionRequest,
)


class EngineeringCatalogService:
    def __init__(self, repository: EngineeringCatalogRepository) -> None:
        self.repository = repository

    def create(self, payload: CatalogItemCreate, user_id: str) -> EngineeringCatalogItem:
        return self.repository.add(
            EngineeringCatalogItem(**payload.model_dump(mode="json"), created_by=user_id)
        )

    def select(self, payload: SelectionRequest) -> PreliminarySelection:
        expected = (
            (payload.material_id, CatalogKind.MATERIAL),
            (payload.machine_id, CatalogKind.MACHINE),
            (payload.tool_id, CatalogKind.TOOL),
        )
        items: list[EngineeringCatalogItem] = []
        for item_id, kind in expected:
            item = self.repository.get(item_id)
            if item is None or item.kind != kind.value:
                raise HTTPException(
                    status_code=404, detail=f"{kind.value.title()} catalog item not found"
                )
            items.append(item)
        material, machine, tool = items
        return PreliminarySelection(
            operation=payload.operation,
            material=CatalogItemRead.model_validate(material),
            machine=CatalogItemRead.model_validate(machine),
            tool=CatalogItemRead.model_validate(tool),
            traceability=[
                f"{item.kind}:{item.code}@{item.data_version}:{item.source}" for item in items
            ],
            limitations=[
                "No toolpath or executable G-code is generated.",
                "Compatibility and process limits require qualified human validation.",
            ],
        )
