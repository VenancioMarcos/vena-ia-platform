"""Ensures every ORM model is imported so `Base.metadata` is fully populated.

Import this module (not the individual model modules) wherever the complete
set of tables is needed: application startup, Alembic migrations and tests.
"""

from app.modules.chats.models import Chat, Message  # noqa: F401
from app.modules.documents.models import Document, DocumentChunk  # noqa: F401
from app.modules.files.models import FileAsset  # noqa: F401
from app.modules.projects.models import Project  # noqa: F401
from app.modules.research.models import (  # noqa: F401
    ANOVADataset,
    DOEStudy,
    ResearchArticle,
    ResearchReference,
    ResearchReport,
)
from app.modules.users.models import User  # noqa: F401
