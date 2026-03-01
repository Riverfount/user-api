"""
Configuração do engine e da SessionFactory do SQLAlchemy.
A URL de conexão é montada dinamicamente a partir das settings do dynaconf.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.core.config import settings


def _build_database_url() -> str:
    """
    Constrói a URL de conexão com base nas configurações do dynaconf.
    Suporta PostgreSQL (padrão) e SQLite (para testes).
    """
    db = settings.database
    driver = db.db_driver

    if driver == "sqlite" or "sqlite" in driver:
        return f"sqlite:///{db.db_name}"

    return (
        f"{driver}://{db.db_user}:{db.db_password}"
        f"@{db.db_host}:{db.db_port}/{db.db_name}"
    )


def create_db_engine():
    """Cria e retorna o engine do SQLAlchemy."""
    url = _build_database_url()
    db = settings.database
    is_sqlite = "sqlite" in url

    kwargs = {
        "echo": db.db_echo,
    }

    if not is_sqlite:
        kwargs["pool_size"] = db.db_pool_size
        kwargs["max_overflow"] = db.db_max_overflow

    engine = create_engine(url, **kwargs)

    if is_sqlite:
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, _connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


# Engine e SessionFactory globais (instanciados uma vez)
engine = create_db_engine()

SessionFactory = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependência FastAPI que fornece uma sessão isolada por request.

    - Commit automático ao final do request bem-sucedido.
    - Rollback automático em caso de exceção.
    - Close garantido pelo bloco finally.
    """
    session: Session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
