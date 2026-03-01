"""
Container de Injeção de Dependências usando o dependency-injector.

Hierarquia de providers:
  SessionFactory  →  Repositories  →  Services

O container é inicializado uma única vez na startup da aplicação
e disponibilizado via app.state para as rotas do FastAPI.
"""

from dependency_injector import containers, providers
from sqlalchemy.orm import Session

from app.db.session import SessionFactory
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """Container IoC principal da aplicação."""

    # ------------------------------------------------------------------
    # Infraestrutura: sessão do banco de dados
    # ------------------------------------------------------------------
    db_session: providers.Factory[Session] = providers.Factory(SessionFactory)

    # ------------------------------------------------------------------
    # Repositórios (Factory → nova instância por injeção)
    # ------------------------------------------------------------------
    user_repository: providers.Factory[UserRepository] = providers.Factory(
        UserRepository,
        session=db_session,
    )

    role_repository: providers.Factory[RoleRepository] = providers.Factory(
        RoleRepository,
        session=db_session,
    )

    # ------------------------------------------------------------------
    # Serviços
    # ------------------------------------------------------------------
    user_service: providers.Factory[UserService] = providers.Factory(
        UserService,
        user_repository=user_repository,
        role_repository=role_repository,
    )
