"""
Importa todos os modelos para que o Alembic os detecte automaticamente
durante a geração de migrations.
"""

from app.models.role import Role
from app.models.claim import Claim
from app.models.user import User, user_claims_table

__all__ = ["Role", "Claim", "User", "user_claims_table"]
