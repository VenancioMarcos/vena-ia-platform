"""Ensures every ORM model is imported so `Base.metadata` is fully populated.

Import this module (not the individual model modules) wherever the complete
set of tables is needed: application startup, Alembic migrations and tests.
"""

from app.modules.chats.models import Chat, Message  # noqa: F401
from app.modules.files.models import FileAsset  # noqa: F401
from app.modules.projects.models import Project  # noqa: F401
from app.modules.users.models import User  # noqa: F401
