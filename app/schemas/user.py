"""
Schemas Pydantic para User.

Separamos claramente:
- UserCreate         → payload de entrada (POST /users)
- UserUpdate         → payload de atualização parcial (PATCH /users/{id})
- UserResponse       → payload de saída (sem a senha)
- UserCreatedResponse → resposta de criação, inclui a senha gerada (se auto-gerada)
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.role import RoleResponse


class UserCreate(BaseModel):
    """
    Payload de criação de usuário.

    - name, email e role_id são obrigatórios.
    - password é opcional: se não informado, será gerado automaticamente pela API.
    """

    name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        examples=["Maria Silva"],
        description="Nome completo do usuário.",
    )
    email: EmailStr = Field(
        ...,
        examples=["maria.silva@example.com"],
        description="E-mail único do usuário.",
    )
    role_id: UUID = Field(
        ...,
        examples=["a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"],
        description="ID do papel (role) do usuário.",
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=128,
        examples=["MinhaSenh@123"],
        description=(
            "Senha do usuário. Se não informada, "
            "uma senha segura será gerada automaticamente."
        ),
    )

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserUpdate(BaseModel):
    """Payload de atualização parcial de usuário. Todos os campos são opcionais."""

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150,
        description="Novo nome do usuário.",
    )
    role_id: UUID | None = Field(
        default=None,
        description="Novo ID do papel (role) do usuário.",
    )
    is_active: bool | None = Field(
        default=None,
        description="Ativa ou desativa o usuário.",
    )


class UserResponse(BaseModel):
    """Representação pública de um usuário (sem expor a senha hasheada)."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    email: EmailStr
    role_id: UUID
    role: RoleResponse | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserCreatedResponse(UserResponse):
    """
    Resposta retornada ao criar um usuário.

    O campo `generated_password` só é preenchido quando a API
    gerou a senha automaticamente — nesse caso, é a ÚNICA vez em que
    a senha em texto plano é retornada. O cliente deve armazená-la.
    """

    generated_password: str | None = Field(
        default=None,
        description=(
            "Senha gerada automaticamente pela API. "
            "Retornada apenas uma vez, na criação. "
            "Null se o usuário forneceu a própria senha."
        ),
    )
