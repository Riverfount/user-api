"""
Repositório para a entidade User.
Encapsula todas as queries relacionadas a usuários.
"""

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.orm import Session, joinedload

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):

    def __init__(self, session: Session) -> None:
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        """Busca um usuário pelo e-mail (case-insensitive)."""
        return (
            self.session.query(User)
            .filter(User.email == email.lower())
            .first()
        )

    def get_by_id_with_role(self, user_id: UUID) -> User | None:
        """Busca um usuário pelo ID, carregando o relacionamento Role com eager loading."""
        return (
            self.session.query(User)
            .options(joinedload(User.role))
            .filter(User.id == user_id)
            .first()
        )

    def get_all_with_roles(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Lista usuários com seus roles carregados via eager loading."""
        return (
            self.session.query(User)
            .options(joinedload(User.role))
            .offset(skip)
            .limit(limit)
            .all()
        )

    def email_exists(self, email: str) -> bool:
        """Verifica existência de e-mail com SELECT EXISTS — sem carregar o objeto."""
        return bool(
            self.session.scalar(
                select(exists().where(User.email == email.lower()))
            )
        )
