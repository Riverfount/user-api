"""
Testes de integração dos endpoints de usuários e autenticação.
"""

from uuid import uuid4
from fastapi.testclient import TestClient


class TestPostUsers:

    def test_cria_usuario_com_senha(self, client: TestClient, seed_role):
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "Bruno Ferreira",
                "email": "bruno@test.com",
                "role_id": str(seed_role.id),
                "password": "Senh@Forte1",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "bruno@test.com"
        assert data["generated_password"] is None
        assert data["is_active"] is True
        assert "password" not in data

    def test_cria_usuario_sem_senha_retorna_senha_gerada(
        self, client: TestClient, seed_role
    ):
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "Camila Torres",
                "email": "camila@test.com",
                "role_id": str(seed_role.id),
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["generated_password"] is not None
        assert len(data["generated_password"]) >= 8

    def test_email_duplicado_retorna_409(self, client: TestClient, seed_role):
        payload = {
            "name": "Diego Lopes",
            "email": "diego@test.com",
            "role_id": str(seed_role.id),
        }
        client.post("/api/v1/users/", json=payload)
        response = client.post("/api/v1/users/", json=payload)
        assert response.status_code == 409

    def test_campos_obrigatorios_ausentes_retorna_422(self, client: TestClient):
        response = client.post("/api/v1/users/", json={"name": "Sem Email"})
        assert response.status_code == 422

    def test_email_invalido_retorna_422(self, client: TestClient, seed_role):
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "Email Inválido",
                "email": "nao-e-um-email",
                "role_id": str(seed_role.id),
            },
        )
        assert response.status_code == 422

    def test_role_inexistente_retorna_422(self, client: TestClient):
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "Fulano",
                "email": "fulano@test.com",
                "role_id": str(uuid4()),
            },
        )
        assert response.status_code == 422

    def test_email_normalizado_para_minusculo(self, client: TestClient, seed_role):
        response = client.post(
            "/api/v1/users/",
            json={
                "name": "Maiusculo",
                "email": "MAIUSCULO@TEST.COM",
                "role_id": str(seed_role.id),
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == "maiusculo@test.com"


class TestGetUser:

    def test_retorna_usuario_existente(self, client: TestClient, seed_role, auth_token: str):
        create_resp = client.post(
            "/api/v1/users/",
            json={
                "name": "Get Teste",
                "email": "getteste@test.com",
                "role_id": str(seed_role.id),
            },
        )
        user_id = create_resp.json()["id"]

        response = client.get(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "getteste@test.com"
        assert data["role"] is not None
        assert "password" not in data

    def test_usuario_inexistente_retorna_404(self, client: TestClient, auth_token: str):
        response = client.get(
            f"/api/v1/users/{uuid4()}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404

    def test_sem_token_retorna_401(self, client: TestClient):
        response = client.get(f"/api/v1/users/{uuid4()}")
        assert response.status_code == 401


class TestListUsers:

    def test_lista_usuarios_autenticado(self, client: TestClient, seed_role, auth_token: str):
        client.post(
            "/api/v1/users/",
            json={
                "name": "Lista User",
                "email": "lista@test.com",
                "role_id": str(seed_role.id),
            },
        )
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_paginacao(self, client: TestClient, auth_token: str):
        response = client.get(
            "/api/v1/users/?skip=0&limit=2",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert len(response.json()) <= 2

    def test_sem_token_retorna_401(self, client: TestClient):
        response = client.get("/api/v1/users/")
        assert response.status_code == 401


class TestUpdateUser:

    def test_atualiza_nome(self, client: TestClient, seed_role, auth_token: str):
        create_resp = client.post(
            "/api/v1/users/",
            json={
                "name": "Nome Original",
                "email": "atualizar@test.com",
                "role_id": str(seed_role.id),
            },
        )
        user_id = create_resp.json()["id"]

        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"name": "Nome Atualizado"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Nome Atualizado"

    def test_desativa_usuario(self, client: TestClient, seed_role, auth_token: str):
        create_resp = client.post(
            "/api/v1/users/",
            json={
                "name": "Para Desativar",
                "email": "desativar@test.com",
                "role_id": str(seed_role.id),
            },
        )
        user_id = create_resp.json()["id"]

        response = client.patch(
            f"/api/v1/users/{user_id}",
            json={"is_active": False},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        assert response.json()["is_active"] is False

    def test_usuario_inexistente_retorna_404(self, client: TestClient, auth_token: str):
        response = client.patch(
            f"/api/v1/users/{uuid4()}",
            json={"name": "Nao existe"},
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 404

    def test_sem_token_retorna_401(self, client: TestClient):
        response = client.patch(f"/api/v1/users/{uuid4()}", json={"name": "x"})
        assert response.status_code == 401


class TestAuthToken:

    def test_login_valido_retorna_token(self, client: TestClient, seed_role, db_session):
        from app.core.security import hash_password
        from app.models.user import User

        user = User(
            name="Login Teste",
            email="login@test.com",
            password=hash_password("Senh@Valid1"),
            role_id=seed_role.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

        response = client.post(
            "/api/v1/auth/token",
            json={"email": "login@test.com", "password": "Senh@Valid1"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_senha_errada_retorna_401(self, client: TestClient, seed_role, db_session):
        from app.core.security import hash_password
        from app.models.user import User

        user = User(
            name="Senha Errada",
            email="senhaerrada@test.com",
            password=hash_password("Senh@Valid1"),
            role_id=seed_role.id,
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()

        response = client.post(
            "/api/v1/auth/token",
            json={"email": "senhaerrada@test.com", "password": "SenhaErrada9"},
        )
        assert response.status_code == 401

    def test_usuario_inexistente_retorna_401(self, client: TestClient):
        response = client.post(
            "/api/v1/auth/token",
            json={"email": "naoexiste@test.com", "password": "qualquer"},
        )
        assert response.status_code == 401
