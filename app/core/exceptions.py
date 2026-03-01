"""
Exceções de domínio da aplicação.

A camada de serviço lança estas exceções; a camada HTTP as traduz
para respostas adequadas via exception handlers registrados em main.py.
"""


from uuid import UUID


class AppError(Exception):
    """Classe base para todas as exceções de domínio."""


class EmailAlreadyExistsError(AppError):
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"E-mail '{email}' já está em uso.")


class RoleNotFoundError(AppError):
    def __init__(self, role_id: UUID) -> None:
        self.role_id = role_id
        super().__init__(f"Role com id={role_id} não encontrado.")


class UserNotFoundError(AppError):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(f"Usuário com id={user_id} não encontrado.")


class InvalidCredentialsError(AppError):
    def __init__(self) -> None:
        super().__init__("E-mail ou senha inválidos.")
