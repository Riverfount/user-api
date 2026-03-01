"""
Serviço de negócio para criação e gerenciamento de usuários.

Responsabilidades:
- Validação de regras de negócio (e-mail único, role existente)
- Geração automática de senha quando não informada
- Hash da senha antes de persistir
- Orquestração entre repositórios

Levanta exceções de domínio (app.core.exceptions) — nunca HTTPException.
"""

from dataclasses import dataclass
from uuid import UUID

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    RoleNotFoundError,
    UserNotFoundError,
)
from app.core.security import generate_password, hash_password, verify_password
from app.models.user import User
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate


@dataclass
class CreateUserResult:
    """Encapsula o resultado da criação: o User persistido + senha gerada (se auto)."""

    user: User
    generated_password: str | None  # None = usuário forneceu a própria senha


class UserService:
    """
    Serviço de usuários injetado via dependency-injector.
    Recebe os repositórios por injeção de dependência.
    """

    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
    ) -> None:
        self._users = user_repository
        self._roles = role_repository

    # ------------------------------------------------------------------
    # Criar usuário
    # ------------------------------------------------------------------
    def create_user(self, payload: UserCreate) -> CreateUserResult:
        """
        Cria um novo usuário aplicando as regras de negócio:

        1. Verifica se o e-mail já está em uso.
        2. Verifica se o role_id existe.
        3. Gera senha automaticamente se não informada.
        4. Faz hash da senha.
        5. Persiste o usuário.
        6. Retorna o usuário criado + senha gerada (quando aplicável).
        """
        if self._users.email_exists(payload.email):
            raise EmailAlreadyExistsError(payload.email)

        role = self._roles.get_by_id(payload.role_id)
        if role is None:
            raise RoleNotFoundError(payload.role_id)

        plain_password = payload.password
        generated_password: str | None = None

        if plain_password is None:
            plain_password = generate_password()
            generated_password = plain_password

        hashed = hash_password(plain_password)

        user = User(
            name=payload.name,
            email=payload.email,  # já normalizado pelo field_validator do schema
            password=hashed,
            role_id=payload.role_id,
        )
        created = self._users.add(user)

        return CreateUserResult(user=created, generated_password=generated_password)

    # ------------------------------------------------------------------
    # Buscar usuário por ID
    # ------------------------------------------------------------------
    def get_user_by_id(self, user_id: UUID) -> User:
        user = self._users.get_by_id_with_role(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    # ------------------------------------------------------------------
    # Listar usuários
    # ------------------------------------------------------------------
    def list_users(self, skip: int = 0, limit: int = 100) -> list[User]:
        return self._users.get_all_with_roles(skip=skip, limit=limit)

    # ------------------------------------------------------------------
    # Atualizar usuário
    # ------------------------------------------------------------------
    def update_user(self, user_id: UUID, payload: UserUpdate) -> User:
        """
        Atualiza parcialmente um usuário.
        Apenas os campos presentes (não None) são modificados.
        """
        user = self._users.get_by_id_with_role(user_id)
        if user is None:
            raise UserNotFoundError(user_id)

        if payload.name is not None:
            user.name = payload.name

        if payload.role_id is not None:
            role = self._roles.get_by_id(payload.role_id)
            if role is None:
                raise RoleNotFoundError(payload.role_id)
            user.role_id = payload.role_id

        if payload.is_active is not None:
            user.is_active = payload.is_active

        self._users.session.flush()
        self._users.session.refresh(user)
        return user

    # ------------------------------------------------------------------
    # Autenticar usuário
    # ------------------------------------------------------------------
    def authenticate_user(self, email: str, password: str) -> User:
        """Verifica credenciais e retorna o usuário autenticado."""
        user = self._users.get_by_email(email.lower())
        if user is None or not verify_password(password, user.password):
            raise InvalidCredentialsError()
        if not user.is_active:
            raise InvalidCredentialsError()
        return user
