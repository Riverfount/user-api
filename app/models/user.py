"""
Modelo SQLAlchemy para a tabela `users`.
Inclui a tabela associativa `user_claims` (many-to-many com claims).
"""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    Table,
    Column,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


# ---------------------------------------------------------------------------
# Tabela associativa user_claims (sem modelo próprio, pois só tem as FKs)
# ---------------------------------------------------------------------------
user_claims_table = Table(
    "user_claims",
    Base.metadata,
    Column(
        "user_id",
        Uuid,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "claim_id",
        Uuid,
        ForeignKey("claims.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# ---------------------------------------------------------------------------
# Modelo User
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)

    role_id: Mapped[UUID] = mapped_column(
        Uuid,
        ForeignKey("roles.id", ondelete="RESTRICT"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # --- Relacionamentos ---
    role: Mapped["Role"] = relationship("Role", back_populates="users")  # noqa: F821

    claims: Mapped[list["Claim"]] = relationship(  # noqa: F821
        "Claim",
        secondary=user_claims_table,
        back_populates="users",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r} role_id={self.role_id}>"
