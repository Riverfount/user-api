"""
Utilitários de autenticação JWT.

- create_access_token : gera um token assinado com HS256
- decode_access_token : verifica e decodifica o token
- get_current_user_email : dependência FastAPI para rotas protegidas
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

bearer_scheme = HTTPBearer()


def create_access_token(subject: str) -> str:
    """Gera um JWT com o e-mail do usuário como subject."""
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.security.access_token_expire_minutes
    )
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.security.secret_key, algorithm="HS256")


def decode_access_token(token: str) -> str:
    """Decodifica o JWT e retorna o subject (e-mail). Lança 401 em caso de falha."""
    try:
        payload = jwt.decode(
            token, settings.security.secret_key, algorithms=["HS256"]
        )
        subject: str | None = payload.get("sub")
        if subject is None:
            raise ValueError("subject ausente")
        return subject
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user_email(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
) -> str:
    """Dependência FastAPI: valida o Bearer token e retorna o e-mail do usuário."""
    return decode_access_token(credentials.credentials)
