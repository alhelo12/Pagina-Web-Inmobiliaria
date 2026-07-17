from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestAuthRegistration:
    """Tests para registro y login"""

    def test_register_client_only(self):
        """Registro público solo permite crear clientes"""
        response = client.post(
            "/auth/register",
            json={
                "full_name": "Juan Pérez",
                "email": "juan@test.com",
                "password": "Password123",
                "phone": "5551234567",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"]["name"] == "client"
        assert data["email"] == "juan@test.com"

    def test_register_cannot_create_admin(self):
        """No se puede crear admin vía registro público"""
        response = client.post(
            "/auth/register",
            json={
                "full_name": "Hacker",
                "email": "hacker@test.com",
                "password": "Password123",
                "phone": "5551234567",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["role"]["name"] == "client"

    def test_register_duplicate_email_fails(self):
        """Email duplicado falla"""
        client.post(
            "/auth/register",
            json={
                "full_name": "Juan Pérez",
                "email": "juan@test.com",
                "password": "Password123",
            },
        )
        response = client.post(
            "/auth/register",
            json={
                "full_name": "Otro Juan",
                "email": "juan@test.com",
                "password": "Password123",
            },
        )
        assert response.status_code == 400
        assert "ya está registrado" in response.json()["detail"]

    def test_login_valid_credentials(self):
        """Login con credenciales válidas"""
        client.post(
            "/auth/register",
            json={
                "full_name": "Juan Pérez",
                "email": "juan@test.com",
                "password": "Password123",
            },
        )
        response = client.post(
            "/auth/login",
            data={"username": "juan@test.com", "password": "Password123"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Login con credenciales inválidas falla"""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent@test.com", "password": "WrongPass"},
        )
        assert response.status_code == 401


class TestAuthTokenHandling:
    """Tests para manejo de tokens"""

    def test_get_me_with_valid_token(self):
        """GET /auth/me con token válido"""
        client.post(
            "/auth/register",
            json={
                "full_name": "Juan Pérez",
                "email": "juan@test.com",
                "password": "Password123",
            },
        )
        login = client.post(
            "/auth/login",
            data={"username": "juan@test.com", "password": "Password123"},
        )
        token = login.json()["access_token"]

        response = client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == "juan@test.com"

    def test_get_me_without_token_fails(self):
        """GET /auth/me sin token falla"""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token_fails(self):
        """GET /auth/me con token inválido falla"""
        response = client.get(
            "/auth/me", headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401


class TestPasswordReset:
    """Tests para recuperación de contraseña"""

    def test_forgot_password_returns_generic_message(self):
        """forgot-password siempre devuelve mensaje genérico"""
        response = client.post(
            "/auth/forgot-password", json={"email": "nonexistent@test.com"}
        )
        assert response.status_code == 200
        assert "Si el email existe" in response.json()["message"]