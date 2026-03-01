"""
Repositório para a entidade Role.
"""

from sqlalchemy.orm import Session

from app.models.role import Role
from app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):

    def __init__(self, session: Session) -> None:
        super().__init__(Role, session)

    def get_by_description(self, description: str) -> Role | None:
        return (
            self.session.query(Role)
            .filter(Role.description == description)
            .first()
        )
