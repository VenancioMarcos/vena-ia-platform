from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.auth.dependencies import CurrentUserDependency
from app.modules.organizations.repository import OrganizationRepository
from app.modules.organizations.service import OrganizationService


def get_organization_service(
    current_user: CurrentUserDependency,
    db: Annotated[Session, Depends(get_db)],
) -> OrganizationService:
    return OrganizationService(OrganizationRepository(db), current_user)


OrganizationServiceDependency = Annotated[
    OrganizationService, Depends(get_organization_service)
]
