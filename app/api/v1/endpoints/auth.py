"""
Endpoint de autenticação — POST /api/v1/auth/token
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.auth import create_access_token
from app.db.session import get_db_session
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/auth", tags=["Auth"])


def _get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    return UserService(
        user_repository=UserRepository(session=session),
        role_repository=RoleRepository(session=session),
    )


@router.post(
    "/token",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Obter token de acesso",
    description="Autentica com e-mail e senha e retorna um Bearer token JWT.",
    responses={
        200: {"description": "Token gerado com sucesso."},
        401: {"description": "Credenciais inválidas ou usuário inativo."},
    },
)
def login(
    payload: LoginRequest,
    service: UserService = Depends(_get_user_service),
) -> TokenResponse:
    """Valida credenciais e emite um token JWT."""
    user = service.authenticate_user(payload.email, payload.password)
    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)
