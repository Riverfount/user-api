"""
Fixtures globais do pytest.

Usa SQLite em memória (compartilhada) para isolar os testes do banco real.
O ambiente 'testing' é ativado via ENV_FOR_DYNACONF antes de qualquer import.
"""

import os

# Define o ambiente ANTES de qualquer import da aplicação
os.environ["ENV_FOR_USERAPI"] = "testing"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.db.base import Base
from app.db.session import get_db_session
from app.main import create_app
from app.repositories.role_repository import RoleRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

# ---------------------------------------------------------------------------
# Engine SQLite in-memory compartilhada entre conexões (necessário para o
# TestClient que roda em thread separada)
# ---------------------------------------------------------------------------
SQLITE_URL = "sqlite:///file:testdb?mode=memory&cache=shared&uri=true"

test_engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_fk(dbapi_conn, _):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


TestSessionFactory = sessionmaker(
    bind=test_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Cria todas as tabelas no banco de testes uma única vez por sessão."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def db_session() -> Session:
    """Fornece uma sessão limpa por teste, com rollback automático."""
    session = TestSessionFactory()
    try:
        yield session
        session.rollback()
    finally:
        session.close()


@pytest.fixture()
def seed_role(db_session: Session):
    """Insere um role padrão para uso nos testes."""
    from app.models.role import Role

    role = Role(description="user")
    db_session.add(role)
    db_session.flush()
    db_session.refresh(role)
    return role


@pytest.fixture()
def user_service(db_session: Session) -> UserService:
    """Instancia o UserService com repositórios apontando para o banco de testes."""
    return UserService(
        user_repository=UserRepository(session=db_session),
        role_repository=RoleRepository(session=db_session),
    )


@pytest.fixture()
def client(db_session: Session) -> TestClient:
    """
    TestClient do FastAPI com get_db_session sobrescrito via dependency_overrides
    para usar a sessão de testes (sem commit — o rollback é feito pelo fixture db_session).
    """
    app = create_app()

    def override_session():
        yield db_session

    app.dependency_overrides[get_db_session] = override_session

    with TestClient(app) as c:
        yield c


@pytest.fixture()
def auth_token(client: TestClient, seed_role, db_session: Session) -> str:
    """Cria um usuário, faz login e retorna o Bearer token para testes autenticados."""
    from app.core.security import hash_password
    from app.models.user import User

    user = User(
        name="Admin Teste",
        email="admin@test.com",
        password=hash_password("Admin@Senha1"),
        role_id=seed_role.id,
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()

    response = client.post(
        "/api/v1/auth/token",
        json={"email": "admin@test.com", "password": "Admin@Senha1"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
