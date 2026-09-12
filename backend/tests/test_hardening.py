"""Checks de endurecimiento: validación de imágenes, DTOs públicos sin PII,
authz de citas, enumeración de emails y manejo de credenciales."""

from datetime import datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.controllers.propertyController import _is_valid_image_header
from app.main import app
from app.models import Advisor, Appointment, Property, Role, User
from app.schemas import AdvisorPublicResponse, PublicPropertyResponse
from app.services.authService import validate_password_strength, verify_password

client = TestClient(app)


def test_image_header_accepts_only_real_signatures():
    assert _is_valid_image_header(b"\xff\xd8\xff\xe0" + b"\x00" * 12)  # JPEG
    assert _is_valid_image_header(b"\x89PNG\r\n\x1a\n" + b"\x00" * 8)  # PNG
    assert _is_valid_image_header(b"RIFF\x00\x00\x00\x00WEBP")  # WebP
    assert not _is_valid_image_header(b"<html>" + b"\x00" * 10)
    assert not _is_valid_image_header(b"RIFF\x00\x00\x00\x00WAVE")
    assert not _is_valid_image_header(b"")


def _user(user_id: int, email: str) -> User:
    user = User()
    user.id = user_id
    user.full_name = "Nombre Test"
    user.email = email
    user.phone = "5550000000"
    user.password_hash = "SECRET_HASH"
    return user


def test_public_advisor_response_excludes_password_hash():
    advisor = Advisor()
    advisor.id = 1
    advisor.user_id = 2
    advisor.rating = 5
    advisor.created_at = datetime.now()
    advisor.updated_at = datetime.now()
    advisor.user = _user(2, "asesor@test.com")

    out = AdvisorPublicResponse.model_validate(advisor).model_dump()
    serialized = str(out)
    assert "SECRET_HASH" not in serialized
    assert "asesor@test.com" not in serialized
    assert "5550000000" not in serialized
    assert out["user"] == {"id": 2, "full_name": "Nombre Test"}


def test_public_property_response_excludes_contact_data():
    prop = Property()
    prop.id = 1
    prop.title = "Casa de prueba"
    prop.price = 1000
    prop.property_type = "house"
    prop.transaction_type = "sale"
    prop.address = "Calle 1"
    prop.city = "CDMX"
    prop.status = "approved"
    prop.bedrooms = 2
    prop.bathrooms = 1
    prop.square_meters = 80
    prop.created_at = datetime.now()
    prop.updated_at = datetime.now()
    prop.owner = _user(2, "dueno@test.com")

    out = PublicPropertyResponse.model_validate(prop).model_dump()
    serialized = str(out)
    assert "dueno@test.com" not in serialized
    assert "5550000000" not in serialized
    assert out["owner"] == {"id": 2, "full_name": "Nombre Test"}


def test_verify_password_handles_malformed_hash():
    assert verify_password("Password123", "no-es-un-hash") is False


def test_password_over_72_bytes_rejected():
    assert validate_password_strength("a" * 71 + "1") is True
    with pytest.raises(HTTPException):
        validate_password_strength("a" * 79 + "1")


def test_token_with_non_numeric_sub_returns_401():
    from app.core.security import create_access_token

    token = create_access_token({"sub": "no-es-entero"})
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_send_verification_does_not_enumerate_emails():
    response = client.post(
        "/auth/send-verification",
        json={"email": f"nadie-{uuid4().hex[:8]}@example.com"},
    )
    assert response.status_code == 200
    assert "token" not in response.json()


def test_property_appointments_restricted_to_assigned_advisor():
    from app.core.security import create_token_for_user
    from app.dbConfig.databaseSession import SessionLocal

    suffix = uuid4().hex[:8]
    db = SessionLocal()
    try:
        advisor_role = db.query(Role).filter(Role.name == "advisor").first()
        client_role = db.query(Role).filter(Role.name == "client").first()
        assert advisor_role and client_role

        advisor1_user = User(
            full_name="Asesor Uno",
            email=f"asesor1-{suffix}@test.com",
            password_hash="x",
            role_id=advisor_role.id,
            is_active=True,
        )
        advisor2_user = User(
            full_name="Asesor Dos",
            email=f"asesor2-{suffix}@test.com",
            password_hash="x",
            role_id=advisor_role.id,
            is_active=True,
        )
        client_user = User(
            full_name="Cliente Cita",
            email=f"cliente-{suffix}@test.com",
            password_hash="x",
            role_id=client_role.id,
            is_active=True,
        )
        db.add_all([advisor1_user, advisor2_user, client_user])
        db.commit()
        for user in (advisor1_user, advisor2_user, client_user):
            db.refresh(user)

        advisor1 = Advisor(user_id=advisor1_user.id)
        advisor2 = Advisor(user_id=advisor2_user.id)
        db.add_all([advisor1, advisor2])
        db.commit()
        db.refresh(advisor1)
        db.refresh(advisor2)

        prop = Property(
            title="Propiedad con citas",
            price=1000,
            property_type="house",
            transaction_type="sale",
            status="approved",
            address="Calle 1",
            city="CDMX",
            submitted_by_user_id=client_user.id,
            advisor_id=advisor1.id,
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)

        db.add(
            Appointment(
                client_id=client_user.id,
                advisor_id=advisor1.id,
                property_id=prop.id,
                scheduled_date=datetime.now(),
                status="pending",
            )
        )
        db.commit()

        token1 = create_token_for_user(advisor1_user.id, advisor1_user.email, "advisor")
        token2 = create_token_for_user(advisor2_user.id, advisor2_user.email, "advisor")
        property_id = prop.id
    finally:
        db.close()

    url = f"/appointments/property/{property_id}/appointments"
    assert client.get(url, headers={"Authorization": f"Bearer {token2}"}).status_code == 403
    assert client.get(url, headers={"Authorization": f"Bearer {token1}"}).status_code == 200
