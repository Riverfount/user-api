"""
Schemas Pydantic para Role.
"""

from pydantic import BaseModel, ConfigDict


class RoleBase(BaseModel):
    description: str


class RoleResponse(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
