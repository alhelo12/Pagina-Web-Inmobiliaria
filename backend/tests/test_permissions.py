import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.main import app

client = TestClient(app)


def get_client_token():
    """Helper: crea usuario cliente y devuelve token"""
    client.post(
        "/auth/register",
        json={
            "full_name": "Cliente Test",
            "email": "cliente@test.com",
            "password": "Password123",
        },
    )
    login = client.post(
        "/auth/login",
        data={"username": "cliente@test.com", "password": "Password123"},
    )
    return login.json()["access_token"]


def get_admin_token():
    """Helper: crea admin directamente en BD (simula admin existente)"""
    from app.dbConfig.databaseSession import SessionLocal
    from app.models import User, Role
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        admin = db.query(User).filter(User.email == "admin@test.com").first()
        if not admin:
            admin = User(
                full_name="Admin Test",
                email="admin@test.com",
                password_hash=hash_password("AdminPass123"),
                role_id=admin_role.id,
                is_active=True,
                is_email_verified=True,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)

        return "AdminPass123"  # password for login
    finally:
        db.close()


def get_advisor_token():
    """Helper: crea asesor y devuelve token"""
    from app.dbConfig.databaseSession import SessionLocal
    from app.models import User, Role, Advisor
    from app.core.security import hash_password

    db = SessionLocal()
    try:
        advisor_role = db.query(Role).filter(Role.name == "advisor").first()
        if not advisor_role:
            advisor_role = Role(name="advisor")
            db.add(advisor_role)
            db.commit()
            db.refresh(advisor_role)

        advisor_user = db.query(User).filter(User.email == "advisor@test.com").first()
        if not advisor_user:
            advisor_user = User(
                full_name="Asesor Test",
                email="advisor@test.com",
                password_hash=hash_password("AdvisorPass123"),
                role_id=advisor_role.id,
                is_active=True,
                is_email_verified=True,
            )
            db.add(advisor_user)
            db.commit()
            db.refresh(advisor_user)

            advisor = Advisor(
                user_id=advisor_user.id,
                license_number="LIC123",
                agency_name="Test Agency",
            )
            db.add(advisor)
            db.commit()

        return "AdvisorPass123"
    finally:
        db.close()


class TestPropertyPermissions:
    """Tests de permisos en propiedades"""

    def test_public_list_only_approved(self):
        """Listado público solo muestra propiedades aprobadas"""
        from app.dbConfig.databaseSession import SessionLocal
        from app.models import Property, User, Role
        from app.core.security import hash_password

        db = SessionLocal()
        try:
            client_role = db.query(Role).filter(Role.name == "client").first()
            user = db.query(User).filter(User.email == "cliente@test.com").first()
            if not user:
                user = User(
                    full_name="Cliente Test",
                    email="cliente@test.com",
                    password_hash=hash_password("Password123"),
                    role_id=client_role.id,
                    is_active=True,
                )
                db.add(user)
                db.commit()
                db.refresh(user)

            # Crear propiedad pendiente
            prop_pending = Property(
                title="Pendiente",
                description="Desc",
                price=100000,
                property_type="house",
                transaction_type="sale",
                status="pending",
                address="Calle 1",
                city="Ciudad",
                submitted_by_user_id=user.id,
            )
            db.add(prop_pending)

            # Crear propiedad aprobada
            prop_approved = Property(
                title="Aprobada",
                description="Desc",
                price=200000,
                property_type="apartment",
                transaction_type="rent",
                status="approved",
                address="Calle 2",
                city="Ciudad",
                submitted_by_user_id=user.id,
            )
            db.add(prop_approved)
            db.commit()
        finally:
            db.close()

        response = client.get("/properties")
        assert response.status_code == 200
        data = response.json()
        titles = [p["title"] for p in data["properties"]]
        assert "Aprobada" in titles
        assert "Pendiente" not in titles

    def test_create_property_requires_auth(self):
        """Crear propiedad requiere autenticación"""
        response = client.post(
            "/properties",
            json={
                "title": "Mi Casa Familiar",
                "description": "Desc",
                "price": 100000,
                "property_type": "house",
                "transaction_type": "sale",
                "address": "Calle Principal 1",
                "city": "Ciudad",
            },
        )
        assert response.status_code == 401

    def test_create_property_with_client_token(self):
        """Cliente autenticado puede crear propiedad"""
        token = get_client_token()
        response = client.post(
            "/properties",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "title": "Mi Casa Familiar",
                "description": "Desc",
                "price": 100000,
                "property_type": "house",
                "transaction_type": "sale",
                "address": "Calle Principal 1",
                "city": "Ciudad",
            },
        )
        assert response.status_code == 201
        assert response.json()["title"] == "Mi Casa Familiar"

    def test_update_property_only_owner(self):
        """Solo el propietario puede actualizar su propiedad"""
        from app.dbConfig.databaseSession import SessionLocal
        from app.models import Property, User, Role
        from app.core.security import hash_password

        db = SessionLocal()
        try:
            client_role = db.query(Role).filter(Role.name == "client").first()
            owner = User(
                full_name="Owner",
                email="owner@test.com",
                password_hash=hash_password("Password123"),
                role_id=client_role.id,
                is_active=True,
            )
            other = User(
                full_name="Other",
                email="other@test.com",
                password_hash=hash_password("Password123"),
                role_id=client_role.id,
                is_active=True,
            )
            db.add_all([owner, other])
            db.commit()
            db.refresh(owner)
            db.refresh(other)

            prop = Property(
                title="Prop Owner",
                description="Desc",
                price=100000,
                property_type="house",
                transaction_type="sale",
                status="approved",
                address="Calle 1",
                city="Ciudad",
                submitted_by_user_id=owner.id,
            )
            db.add(prop)
            db.commit()
            db.refresh(prop)
            prop_id = prop.id
        finally:
            db.close()

        # Owner puede actualizar
        owner_login = client.post(
            "/auth/login",
            data={"username": "owner@test.com", "password": "Password123"},
        )
        owner_token = owner_login.json()["access_token"]

        response = client.put(
            f"/properties/{prop_id}",
            headers={"Authorization": f"Bearer {owner_token}"},
            json={"title": "Updated Title"},
        )
        assert response.status_code == 200

        # Otro usuario no puede
        other_login = client.post(
            "/auth/login",
            data={"username": "other@test.com", "password": "Password123"},
        )
        other_token = other_login.json()["access_token"]

        response = client.put(
            f"/properties/{prop_id}",
            headers={"Authorization": f"Bearer {other_token}"},
            json={"title": "Hacked Title"},
        )
        assert response.status_code == 403


class TestAdvisorPermissions:
    """Tests de permisos de asesor"""

    def test_advisor_cannot_create_advisor_profile(self):
        """Asesor no puede crear perfil de asesor (solo admin)"""
        password = get_advisor_token()
        login = client.post(
            "/auth/login",
            data={"username": "advisor@test.com", "password": password},
        )
        token = login.json()["access_token"]

        response = client.post(
            "/advisors",
            headers={"Authorization": f"Bearer {token}"},
            json={"license_number": "LIC999", "agency_name": "Fake Agency"},
        )
        assert response.status_code == 403

    def test_admin_can_create_advisor_profile(self):
        """Admin puede crear perfil de asesor"""
        get_admin_token()
        from app.dbConfig.databaseSession import SessionLocal
        from app.models import Role, User
        from app.core.security import hash_password

        db = SessionLocal()
        advisor_role = db.query(Role).filter(Role.name == "advisor").first()
        target = User(
            full_name="Nuevo Asesor",
            email="nuevo-asesor@test.com",
            password_hash=hash_password("AdvisorPass123"),
            role_id=advisor_role.id,
            is_active=True,
        )
        db.add(target)
        db.commit()
        db.refresh(target)
        target_id = target.id
        db.close()

        admin_login = client.post(
            "/auth/login",
            data={"username": "admin@test.com", "password": "AdminPass123"},
        )
        admin_token = admin_login.json()["access_token"]

        response = client.post(
            f"/advisors?user_id={target_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={"license_number": "LIC999", "agency_name": "Fake Agency"},
        )
        assert response.status_code == 201

    def test_advisor_can_only_approve_own_properties(self):
        """Asesor solo puede aprobar sus propiedades asignadas"""
        get_advisor_token()
        from app.dbConfig.databaseSession import SessionLocal
        from app.models import Property, User, Role, Advisor
        from app.core.security import hash_password

        db = SessionLocal()
        try:
            advisor_role = db.query(Role).filter(Role.name == "advisor").first()
            advisor_user = db.query(User).filter(User.email == "advisor@test.com").first()
            advisor = db.query(Advisor).filter(Advisor.user_id == advisor_user.id).first()

            # Crear otro asesor
            other_advisor_user = User(
                full_name="Other Advisor",
                email="other_advisor@test.com",
                password_hash=hash_password("Password123"),
                role_id=advisor_role.id,
                is_active=True,
            )
            db.add(other_advisor_user)
            db.commit()
            db.refresh(other_advisor_user)
            other_advisor = Advisor(user_id=other_advisor_user.id)
            db.add(other_advisor)
            db.commit()

            client_role = db.query(Role).filter(Role.name == "client").first()
            client_user = User(
                full_name="Client",
                email="client@test.com",
                password_hash=hash_password("Password123"),
                role_id=client_role.id,
                is_active=True,
            )
            db.add(client_user)
            db.commit()

            # Propiedad asignada al asesor 1
            prop1 = Property(
                title="Prop Advisor 1",
                description="Desc",
                price=100000,
                property_type="house",
                transaction_type="sale",
                status="pending",
                address="Calle 1",
                city="Ciudad",
                submitted_by_user_id=client_user.id,
                advisor_id=advisor.id,
            )
            # Propiedad asignada al asesor 2
            prop2 = Property(
                title="Prop Advisor 2",
                description="Desc",
                price=200000,
                property_type="apartment",
                transaction_type="sale",
                status="pending",
                address="Calle 2",
                city="Ciudad",
                submitted_by_user_id=client_user.id,
                advisor_id=other_advisor.id,
            )
            db.add_all([prop1, prop2])
            db.commit()
            db.refresh(prop1)
            db.refresh(prop2)
            prop1_id, prop2_id = prop1.id, prop2.id
        finally:
            db.close()

        # Login asesor 1
        login = client.post(
            "/auth/login",
            data={"username": "advisor@test.com", "password": "AdvisorPass123"},
        )
        token = login.json()["access_token"]

        # Asesor 1 puede aprobar su propiedad
        response = client.patch(
            f"/properties/{prop1_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # Asesor 1 NO puede aprobar propiedad de asesor 2
        response = client.patch(
            f"/properties/{prop2_id}/approve",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 403


class TestPostSalePermissions:
    """Tests de permisos post-venta"""

    def test_advisor_only_sees_own_followups(self):
        """Asesor solo ve sus seguimientos"""
        get_advisor_token()
        from app.dbConfig.databaseSession import SessionLocal
        from app.models import PostSaleFollowup, User, Role, Advisor, Property
        from app.core.security import hash_password

        db = SessionLocal()
        try:
            advisor_user = db.query(User).filter(User.email == "advisor@test.com").first()
            advisor = db.query(Advisor).filter(Advisor.user_id == advisor_user.id).first()

            # Otro asesor
            advisor_role = db.query(Role).filter(Role.name == "advisor").first()
            other_advisor_user = User(
                full_name="Other Advisor 2",
                email="other_advisor2@test.com",
                password_hash=hash_password("Password123"),
                role_id=advisor_role.id,
                is_active=True,
            )
            db.add(other_advisor_user)
            db.commit()
            other_advisor = Advisor(user_id=other_advisor_user.id)
            db.add(other_advisor)
            db.commit()

            client_role = db.query(Role).filter(Role.name == "client").first()
            client_user = User(
                full_name="Client Followup",
                email="client_followup@test.com",
                password_hash=hash_password("Password123"),
                role_id=client_role.id,
                is_active=True,
            )
            db.add(client_user)
            db.commit()

            prop = Property(
                title="Sold Prop",
                description="Desc",
                price=100000,
                property_type="house",
                transaction_type="sale",
                status="sold",
                address="Calle 1",
                city="Ciudad",
                submitted_by_user_id=client_user.id,
                advisor_id=advisor.id,
            )
            db.add(prop)
            db.commit()
            db.refresh(prop)

            followup1 = PostSaleFollowup(
                property_id=prop.id,
                client_id=client_user.id,
                advisor_id=advisor.id,
                followup_type="check_in_call",
                status="pending",
                sale_date=datetime(2026, 1, 1),
                scheduled_date=datetime(2026, 1, 15, 10),
            )
            followup2 = PostSaleFollowup(
                property_id=prop.id,
                client_id=client_user.id,
                advisor_id=other_advisor.id,
                followup_type="referral_request",
                status="pending",
                sale_date=datetime(2026, 1, 1),
                scheduled_date=datetime(2026, 1, 20, 10),
            )
            db.add_all([followup1, followup2])
            db.commit()
            advisor_id = advisor.id
        finally:
            db.close()

        # Login asesor 1
        login = client.post(
            "/auth/login",
            data={"username": "advisor@test.com", "password": "AdvisorPass123"},
        )
        token = login.json()["access_token"]

        response = client.get(
            "/post-sale/list",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        # Solo debe ver 1 seguimiento (el suyo)
        assert data["total"] == 1
        assert data["followups"][0]["advisor_id"] == advisor_id


class TestWebSocketAuth:
    """Tests básicos de autenticación WebSocket"""

    def test_websocket_rejects_invalid_token(self):
        """WebSocket rechaza token inválido"""
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect("/ws?token=invalid"):
                pass
        assert exc.value.code == 4001

    def test_websocket_requires_token(self):
        """WebSocket requiere token"""
        with pytest.raises(WebSocketDisconnect) as exc:
            with client.websocket_connect("/ws"):
                pass
        assert exc.value.code == 4001
