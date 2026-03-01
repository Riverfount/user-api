"""
Endpoints de usuários — /api/v1/users
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_email
from app.db.session import get_db_session
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserCreatedResponse, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


def _get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    """
    Cria o UserService injetando a mesma sessão em ambos os repositórios.
    O ciclo de vida da sessão (commit/rollback/close) é gerenciado por get_db_session.
    """
    return UserService(
        user_repository=UserRepository(session=session),
        role_repository=RoleRepository(session=session),
    )


@router.post(
    "/",
    response_model=UserCreatedResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Criar usuário",
    description=(
        "Cria um novo usuário. **name**, **email** e **role_id** são obrigatórios. "
        "**password** é opcional: se não informado, uma senha segura é gerada "
        "automaticamente e retornada **apenas nesta resposta**."
    ),
    responses={
        201: {"description": "Usuário criado com sucesso."},
        409: {"description": "E-mail já cadastrado."},
        422: {"description": "Dados inválidos ou role não encontrado."},
    },
)
def create_user(
    payload: UserCreate,
    service: UserService = Depends(_get_user_service),
) -> UserCreatedResponse:
    """
    Endpoint de criação de usuário.

    - Se `password` não for enviado, a API gera automaticamente e o retorna
      no campo `generated_password` da resposta.
    - A senha **nunca** é retornada em consultas posteriores.
    """
    result = service.create_user(payload)
    return UserCreatedResponse.model_validate(result.user).model_copy(
        update={"generated_password": result.generated_password}
    )


@router.get(
    "/",
    response_model=list[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar usuários",
    responses={
        200: {"description": "Lista de usuários."},
        401: {"description": "Não autenticado."},
    },
)
def list_users(
    skip: int = Query(default=0, ge=0, description="Número de registros a pular."),
    limit: int = Query(default=100, ge=1, le=500, description="Máximo de registros."),
    service: UserService = Depends(_get_user_service),
    _current_user: str = Depends(get_current_user_email),
) -> list[UserResponse]:
    """Lista todos os usuários com paginação. Requer autenticação."""
    users = service.list_users(skip=skip, limit=limit)
    return [UserResponse.model_validate(u) for u in users]


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Buscar usuário por ID",
    responses={
        200: {"description": "Usuário encontrado."},
        401: {"description": "Não autenticado."},
        404: {"description": "Usuário não encontrado."},
    },
)
def get_user(
    user_id: int,
    service: UserService = Depends(_get_user_service),
    _current_user: str = Depends(get_current_user_email),
) -> UserResponse:
    """Retorna os dados de um usuário pelo seu ID. Requer autenticação."""
    user = service.get_user_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Atualizar usuário",
    description="Atualiza parcialmente name, role_id e/ou is_active. Requer autenticação.",
    responses={
        200: {"description": "Usuário atualizado."},
        401: {"description": "Não autenticado."},
        404: {"description": "Usuário não encontrado."},
        422: {"description": "Dados inválidos ou role não encontrado."},
    },
)
def update_user(
    user_id: int,
    payload: UserUpdate,
    service: UserService = Depends(_get_user_service),
    _current_user: str = Depends(get_current_user_email),
) -> UserResponse:
    """Atualiza parcialmente um usuário. Requer autenticação."""
    user = service.update_user(user_id, payload)
    return UserResponse.model_validate(user)
