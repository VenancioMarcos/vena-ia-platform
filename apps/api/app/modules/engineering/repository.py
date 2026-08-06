from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.engineering.models import EngineeringCatalogItem


class EngineeringCatalogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(self, item: EngineeringCatalogItem) -> EngineeringCatalogItem:
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def list(self, kind: str | None = None) -> list[EngineeringCatalogItem]:
        stmt = select(EngineeringCatalogItem).order_by(
            EngineeringCatalogItem.kind, EngineeringCatalogItem.code
        )
        if kind is not None:
            stmt = stmt.where(EngineeringCatalogItem.kind == kind)
        return list(self.db.scalars(stmt))

    def get(self, item_id: str) -> EngineeringCatalogItem | None:
        return self.db.get(EngineeringCatalogItem, item_id)
