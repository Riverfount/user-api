"""
Repositório genérico com operações CRUD básicas.
Todos os repositórios concretos herdam desta classe.
"""

from typing import Generic, TypeVar, Type
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Repositório base com operações CRUD genéricas."""

    def __init__(self, model: Type[ModelType], session: Session) -> None:
        self.model = model
        self.session = session

    def get_by_id(self, entity_id: UUID) -> ModelType | None:
        return self.session.get(self.model, entity_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        return (
            self.session.query(self.model)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.flush()   # Popula o id sem fechar a transação
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.session.delete(entity)
        self.session.flush()
