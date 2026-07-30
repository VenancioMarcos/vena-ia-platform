"""Central authorization policies for authenticated users and project resources."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.modules.projects.models import Project
from app.modules.users.models import User


def user_is_admin(user: User) -> bool:
    return user.role == "admin"


def user_can_access_project(user: User, project: Project) -> bool:
    return project.owner_id == user.id or user_is_admin(user)


class AuthorizationService:
    def __init__(self, db: Session, current_user: User) -> None:
        self._db = db
        self.current_user = current_user

    @property
    def is_admin(self) -> bool:
        return user_is_admin(self.current_user)

    def require_admin(self) -> User:
        if not self.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative access required",
            )
        return self.current_user

    def require_user_access(self, user_id: str) -> User:
        user = self._db.get(User, user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        if user.id != self.current_user.id and not self.is_admin:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def require_project_access(self, project_id: str) -> Project:
        project = self._db.get(Project, project_id)
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        if not user_can_access_project(self.current_user, project):
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    def authorized_owner_filter(self, requested_owner_id: str | None) -> str | None:
        if self.is_admin:
            return requested_owner_id
        if requested_owner_id is not None and requested_owner_id != self.current_user.id:
            raise HTTPException(status_code=403, detail="Project access denied")
        return self.current_user.id
