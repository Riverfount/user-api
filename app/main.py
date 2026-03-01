"""
Ponto de entrada da aplicação FastAPI.

Responsabilidades:
- Criação da instância FastAPI
- Inicialização do container IoC (dependency-injector)
- Registro dos routers
- Lifecycle events (startup / shutdown)
- Exception handlers para exceções de domínio
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.containers.container import Container
from app.core.config import settings
from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    RoleNotFoundError,
    UserNotFoundError,
)
from app.api.v1.router import api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gerencia o ciclo de vida da aplicação.
    - startup : inicializa o container IoC
    - shutdown: executa limpeza de recursos
    """
    container = Container()
    app.state.container = container
    print(f"✅  [{settings.current_env.upper()}] {settings.app_name} iniciado.")
    yield
    print("🛑  Encerrando aplicação...")


def _register_exception_handlers(app: FastAPI) -> None:
    """Registra os handlers que traduzem exceções de domínio em respostas HTTP."""

    @app.exception_handler(EmailAlreadyExistsError)
    async def email_conflict(_request: Request, exc: EmailAlreadyExistsError):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(RoleNotFoundError)
    async def role_not_found(_request: Request, exc: RoleNotFoundError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(UserNotFoundError)
    async def user_not_found(_request: Request, exc: UserNotFoundError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(InvalidCredentialsError)
    async def invalid_credentials(_request: Request, exc: InvalidCredentialsError):
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_app() -> FastAPI:
    """Factory que cria e configura a instância FastAPI."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.app_debug,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS — origens configuráveis via settings.toml / variáveis de ambiente
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    _register_exception_handlers(app)

    app.include_router(api_v1_router)

    @app.get("/health", tags=["Health"])
    def health_check():
        return {"status": "ok", "env": settings.current_env}

    return app


app = create_app()
