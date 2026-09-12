"""Checks de endurecimiento: validación de imágenes y DTOs públicos sin PII."""

from datetime import datetime

from app.controllers.propertyController import _is_valid_image_header
from app.models import Advisor, Property, User
from app.schemas import AdvisorPublicResponse, PublicPropertyResponse


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
