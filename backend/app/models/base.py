"""SQLAlchemy declarative base and common mixins."""

from datetime import datetime
from typing import Any, ClassVar
from uuid import UUID

from sqlalchemy import MetaData, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from uuid6 import uuid7

# Naming convention for constraints
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_name)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Schema for all Faceplate tables
FACEPLATE_SCHEMA = "faceplate"


class Base(DeclarativeBase):
    """Base class for all Faceplate models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION, schema=FACEPLATE_SCHEMA)

    # Type annotation map for SQLAlchemy
    type_annotation_map: ClassVar[dict] = {
        UUID: PG_UUID(as_uuid=True),
    }


class UUIDMixin:
    """Mixin that adds a UUID primary key."""

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    )


class TimestampMixin:
    """Mixin that adds created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )


class BaseModel(Base, UUIDMixin):
    """Abstract base model with UUID primary key.

    Use this as the base for all Faceplate models.
    """

    __abstract__ = True

    def __repr__(self) -> str:
        """Return string representation of the model."""
        return f"<{self.__class__.__name__}(id={self.id})>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
