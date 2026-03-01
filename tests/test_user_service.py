"""
Testes unitários do UserService.
"""

import pytest
from uuid import uuid4

from app.core.exceptions import (
    EmailAlreadyExistsError,
    InvalidCredentialsError,
    RoleNotFoundError,
    UserNotFoundError,
)
from app.schemas.user import UserCreate, UserUpdate
from app.services.user_service import UserService


class TestCreateUser:
    """Testes para UserService.create_user()"""

    def test_cria_usuario_com_senha_informada(self, user_service: UserService, seed_role):
        payload = UserCreate(
            name="João Silva",
            email="joao@example.com",
            role_id=seed_role.id,
            password="MinhaSenh@123",
        )
        result = user_service.create_user(payload)

        assert result.user.id is not None
        assert result.user.email == "joao@example.com"
        assert result.generated_password is None

    def test_cria_usuario_sem_senha_gera_automaticamente(
        self, user_service: UserService, seed_role
    ):
        payload = UserCreate(
            name="Ana Costa",
            email="ana@example.com",
            role_id=seed_role.id,
            password=None,
        )
        result = user_service.create_user(payload)

        assert result.user.id is not None
        assert result.generated_password is not None
        assert len(result.generated_password) >= 8

    def test_email_duplicado_levanta_email_already_exists(
        self, user_service: UserService, seed_role
    ):
        payload = UserCreate(
            name="Carlos Dias",
            email="carlos@example.com",
            role_id=seed_role.id,
        )
        user_service.create_user(payload)

        with pytest.raises(EmailAlreadyExistsError) as exc_info:
            user_service.create_user(payload)

        assert "carlos@example.com" in str(exc_info.value)

    def test_role_inexistente_levanta_role_not_found(self, user_service: UserService):
        nonexistent_role_id = uuid4()
        payload = UserCreate(
            name="Maria Nunes",
            email="maria@example.com",
            role_id=nonexistent_role_id,
        )
        with pytest.raises(RoleNotFoundError) as exc_info:
            user_service.create_user(payload)

        assert exc_info.value.role_id == nonexistent_role_id

    def test_senha_armazenada_como_hash(self, user_service: UserService, seed_role):
        from app.core.security import verify_password

        plain = "SenhaSegura#99"
        payload = UserCreate(
            name="Pedro Alves",
            email="pedro@example.com",
            role_id=seed_role.id,
            password=plain,
        )
        result = user_service.create_user(payload)

        assert result.user.password != plain
        assert verify_password(plain, result.user.password)

    def test_email_normalizado_para_minusculo(self, user_service: UserService, seed_role):
        payload = UserCreate(
            name="Lucia Melo",
            email="Lucia.Melo@Example.COM",
            role_id=seed_role.id,
        )
        result = user_service.create_user(payload)

        assert result.user.email == "lucia.melo@example.com"

    def test_usuario_criado_com_is_active_true(self, user_service: UserService, seed_role):
        payload = UserCreate(
            name="Ativo Padrão",
            email="ativo@example.com",
            role_id=seed_role.id,
        )
        result = user_service.create_user(payload)

        assert result.user.is_active is True


class TestGetUserById:
    """Testes para UserService.get_user_by_id()"""

    def test_retorna_usuario_existente(self, user_service: UserService, seed_role):
        payload = UserCreate(
            name="Busca ID",
            email="busca@example.com",
            role_id=seed_role.id,
        )
        created = user_service.create_user(payload).user

        found = user_service.get_user_by_id(created.id)
        assert found.id == created.id
        assert found.role is not None

    def test_usuario_inexistente_levanta_user_not_found(self, user_service: UserService):
        nonexistent_id = uuid4()
        with pytest.raises(UserNotFoundError) as exc_info:
            user_service.get_user_by_id(nonexistent_id)

        assert exc_info.value.user_id == nonexistent_id


class TestUpdateUser:
    """Testes para UserService.update_user()"""

    def test_atualiza_nome(self, user_service: UserService, seed_role):
        created = user_service.create_user(
            UserCreate(name="Nome Antigo", email="update1@example.com", role_id=seed_role.id)
        ).user

        updated = user_service.update_user(created.id, UserUpdate(name="Nome Novo"))
        assert updated.name == "Nome Novo"

    def test_desativa_usuario(self, user_service: UserService, seed_role):
        created = user_service.create_user(
            UserCreate(name="Desativar", email="desativar@example.com", role_id=seed_role.id)
        ).user

        updated = user_service.update_user(created.id, UserUpdate(is_active=False))
        assert updated.is_active is False

    def test_role_inexistente_levanta_role_not_found(self, user_service: UserService, seed_role):
        created = user_service.create_user(
            UserCreate(name="Role Inv", email="roleinv@example.com", role_id=seed_role.id)
        ).user

        with pytest.raises(RoleNotFoundError):
            user_service.update_user(created.id, UserUpdate(role_id=uuid4()))

    def test_usuario_inexistente_levanta_user_not_found(self, user_service: UserService):
        with pytest.raises(UserNotFoundError):
            user_service.update_user(uuid4(), UserUpdate(name="Novo Nome"))


class TestAuthenticateUser:
    """Testes para UserService.authenticate_user()"""

    def test_credenciais_validas_retorna_usuario(self, user_service: UserService, seed_role):
        user_service.create_user(
            UserCreate(
                name="Auth User",
                email="auth@example.com",
                role_id=seed_role.id,
                password="Senh@Valid1",
            )
        )

        user = user_service.authenticate_user("auth@example.com", "Senh@Valid1")
        assert user.email == "auth@example.com"

    def test_senha_errada_levanta_invalid_credentials(
        self, user_service: UserService, seed_role
    ):
        user_service.create_user(
            UserCreate(
                name="Wrong Pass",
                email="wrongpass@example.com",
                role_id=seed_role.id,
                password="Senh@Valid1",
            )
        )

        with pytest.raises(InvalidCredentialsError):
            user_service.authenticate_user("wrongpass@example.com", "SenhaErrada1")

    def test_email_inexistente_levanta_invalid_credentials(self, user_service: UserService):
        with pytest.raises(InvalidCredentialsError):
            user_service.authenticate_user("naoexiste@example.com", "qualquer")

    def test_usuario_inativo_levanta_invalid_credentials(
        self, user_service: UserService, seed_role
    ):
        result = user_service.create_user(
            UserCreate(
                name="Inativo",
                email="inativo@example.com",
                role_id=seed_role.id,
                password="Senh@Valid1",
            )
        )
        user_service.update_user(result.user.id, UserUpdate(is_active=False))

        with pytest.raises(InvalidCredentialsError):
            user_service.authenticate_user("inativo@example.com", "Senh@Valid1")
