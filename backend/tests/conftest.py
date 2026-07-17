import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.core.rateLimiter import limiter
from app.dbConfig import databaseSession
from app.dbConfig.databaseSession import get_db
from app.dbConfig.baseModels import Base
from app.models import Role, User, Advisor
from app.services.authService import hash_password

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function", autouse=True)
def isolate_database(db, monkeypatch):
    monkeypatch.setattr(databaseSession, "SessionLocal", TestingSessionLocal)

    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    limiter.reset()
    db.add_all([
        Role(id=1, name="admin"),
        Role(id=2, name="advisor"),
        Role(id=3, name="client"),
    ])
    db.commit()
    yield
    app.dependency_overrides.clear()
    limiter.reset()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_roles(db):
    roles = [
        Role(id=1, name="admin"),
        Role(id=2, name="advisor"),
        Role(id=3, name="client"),
    ]
    db.add_all(roles)
    db.commit()
    return roles


@pytest.fixture(scope="function")
def test_user(db, test_roles):
    user = User(
        full_name="Test User",
        email="test@example.com",
        password_hash=hash_password("TestPass123"),
        role_id=3,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_user(db, test_roles):
    admin = User(
        full_name="Admin User",
        email="admin@example.com",
        password_hash=hash_password("AdminPass123"),
        role_id=1,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def advisor_user(db, test_roles):
    user = User(
        full_name="Advisor User",
        email="advisor@example.com",
        password_hash=hash_password("AdvisorPass123"),
        role_id=2,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    advisor = Advisor(
        user_id=user.id,
        license_number="LIC123",
        agency_name="Test Agency",
    )
    db.add(advisor)
    db.commit()
    db.refresh(advisor)
    return user, advisor


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/auth/login",
        data={"username": test_user.email, "password": "TestPass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": admin_user.email, "password": "AdminPass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def advisor_headers(client, advisor_user):
    user, _ = advisor_user
    response = client.post(
        "/auth/login",
        data={"username": user.email, "password": "AdvisorPass123"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
