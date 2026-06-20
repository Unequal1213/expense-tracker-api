from collections.abc import Generator

import app.models  # noqa: F401
import pytest
from app.api.dependencies import get_db
from app.database.database import Base
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


@pytest.fixture()
def client() -> Generator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db() -> Generator[Session]:
        db = testing_session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_category(client: TestClient) -> None:
    response = client.post(
        "/categories",
        json={"name": "Salary", "type": "income"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "Salary"
    assert data["type"] == "income"
    assert "created_at" in data
    assert "updated_at" in data


def test_invalid_category_type_returns_422(client: TestClient) -> None:
    response = client.post(
        "/categories",
        json={"name": "Broken", "type": "invalid"},
    )

    assert response.status_code == 422


def test_list_categories(client: TestClient) -> None:
    client.post("/categories", json={"name": "Salary", "type": "income"})
    client.post("/categories", json={"name": "Groceries", "type": "expense"})

    response = client.get("/categories")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Salary"
    assert data[0]["type"] == "income"
    assert data[1]["name"] == "Groceries"
    assert data[1]["type"] == "expense"


def test_get_category_by_id(client: TestClient) -> None:
    create_response = client.post(
        "/categories",
        json={"name": "Salary", "type": "income"},
    )
    category_id = create_response.json()["id"]

    response = client.get(f"/categories/{category_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Salary"
    assert response.json()["type"] == "income"


def test_missing_category_returns_404(client: TestClient) -> None:
    response = client.get("/categories/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_partial_update_preserves_omitted_fields(client: TestClient) -> None:
    create_response = client.post(
        "/categories",
        json={"name": "Food", "type": "expense"},
    )
    category_id = create_response.json()["id"]

    response = client.patch(
        f"/categories/{category_id}",
        json={"name": "Groceries"},
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Groceries"
    assert response.json()["type"] == "expense"


def test_delete_category(client: TestClient) -> None:
    create_response = client.post(
        "/categories",
        json={"name": "Food", "type": "expense"},
    )
    category_id = create_response.json()["id"]

    response = client.delete(f"/categories/{category_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_deleted_category_is_no_longer_returned(client: TestClient) -> None:
    create_response = client.post(
        "/categories",
        json={"name": "Food", "type": "expense"},
    )
    category_id = create_response.json()["id"]

    delete_response = client.delete(f"/categories/{category_id}")
    get_response = client.get(f"/categories/{category_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
