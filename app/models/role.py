"""
Modelo SQLAlchemy para a tabela `roles`.
"""

from uuid import UUID, uuid4

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    description: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)

    # Relacionamento reverso com User
    users: Mapped[list["User"]] = relationship("User", back_populates="role")  # noqa: F821

    def __repr__(self) -> str:
        return f"<Role id={self.id} description={self.description!r}>"
