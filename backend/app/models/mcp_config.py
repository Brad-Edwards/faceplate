"""MCP Config model for Faceplate."""

from datetime import datetime
from typing import TYPE_CHECKING, Any
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User


class MCPConfig(BaseModel):
    """MCP Config model for per-user MCP server configurations."""

    __tablename__ = "mcp_configs"
    __table_args__ = (UniqueConstraint("user_id", "name", name="uq_mcp_configs_user_id_name"),)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("faceplate.users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    config: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
    )
    enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="mcp_configs",
    )

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<MCPConfig(id={self.id}, name={self.name})>"
