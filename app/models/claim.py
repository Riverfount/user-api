"""
Modelo SQLAlchemy para a tabela `claims`.
"""

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # Relacionamento many-to-many com User via user_claims
    users: Mapped[list["User"]] = relationship(  # noqa: F821
        "User",
        secondary="user_claims",
        back_populates="claims",
    )

    def __repr__(self) -> str:
        return f"<Claim id={self.id} description={self.description!r} active={self.active}>"
