from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.modules.research.contracts import ResearchEntity
from app.modules.research.models import (
    ANOVADataset,
    DOEStudy,
    ResearchArticle,
    ResearchReference,
    ResearchReport,
)


class ResearchRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def save(self, entity: ResearchEntity) -> ResearchEntity:
        try:
            self._db.add(entity)
            self._db.commit()
            self._db.refresh(entity)
            return entity
        except Exception:
            self._db.rollback()
            raise

    def delete(self, entity: ResearchEntity) -> None:
        try:
            self._db.delete(entity)
            self._db.commit()
        except Exception:
            self._db.rollback()
            raise

    def get_article(self, article_id: str) -> ResearchArticle | None:
        return self._db.get(ResearchArticle, article_id)

    def list_articles(self, project_id: str) -> list[ResearchArticle]:
        stmt = (
            select(ResearchArticle)
            .where(ResearchArticle.project_id == project_id)
            .order_by(ResearchArticle.created_at)
        )
        return list(self._db.scalars(stmt))

    def replace_references(
        self,
        article_id: str,
        references: list[ResearchReference],
    ) -> list[ResearchReference]:
        try:
            self._db.execute(
                delete(ResearchReference).where(
                    ResearchReference.article_id == article_id
                )
            )
            self._db.add_all(references)
            self._db.commit()
            for reference in references:
                self._db.refresh(reference)
            return references
        except Exception:
            self._db.rollback()
            raise

    def list_references(self, article_id: str) -> list[ResearchReference]:
        stmt = (
            select(ResearchReference)
            .where(ResearchReference.article_id == article_id)
            .order_by(ResearchReference.page_number, ResearchReference.created_at)
        )
        return list(self._db.scalars(stmt))

    def get_doe_study(self, study_id: str) -> DOEStudy | None:
        return self._db.get(DOEStudy, study_id)

    def get_anova_dataset(self, dataset_id: str) -> ANOVADataset | None:
        return self._db.get(ANOVADataset, dataset_id)

    def get_report(self, report_id: str) -> ResearchReport | None:
        return self._db.get(ResearchReport, report_id)

    def list_reports(self, project_id: str) -> list[ResearchReport]:
        stmt = (
            select(ResearchReport)
            .where(ResearchReport.project_id == project_id)
            .order_by(ResearchReport.created_at)
        )
        return list(self._db.scalars(stmt))
