from fastapi.testclient import TestClient


def create_category(client: TestClient) -> int:
    response = client.post(
        "/categories",
        json={"name": "Salary", "type": "income"},
    )
    return response.json()["id"]


def transaction_payload(category_id: int) -> dict[str, str | int]:
    return {
        "category_id": category_id,
        "amount": "125.50",
        "type": "income",
        "description": "Monthly salary",
        "transaction_date": "2026-06-24T12:00:00+03:00",
    }


def test_create_transaction(client: TestClient) -> None:
    category_id = create_category(client)

    response = client.post(
        "/transactions",
        json=transaction_payload(category_id),
    )

    assert response.status_code == 201
    data = response.json()
    assert data["id"] == 1
    assert data["category_id"] == category_id
    assert data["amount"] == "125.50"
    assert data["type"] == "income"
    assert data["description"] == "Monthly salary"
    assert data["transaction_date"].startswith("2026-06-24T12:00:00")
    assert "created_at" in data
    assert "updated_at" in data


def test_create_transaction_with_missing_category_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        "/transactions",
        json=transaction_payload(category_id=999),
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Category not found"}


def test_invalid_transaction_type_returns_422(client: TestClient) -> None:
    category_id = create_category(client)
    payload = transaction_payload(category_id)
    payload["type"] = "invalid"

    response = client.post("/transactions", json=payload)

    assert response.status_code == 422


def test_invalid_amount_returns_422(client: TestClient) -> None:
    category_id = create_category(client)
    payload = transaction_payload(category_id)
    payload["amount"] = "0"

    response = client.post("/transactions", json=payload)

    assert response.status_code == 422


def test_list_transactions(client: TestClient) -> None:
    category_id = create_category(client)
    client.post("/transactions", json=transaction_payload(category_id))
    second_payload = transaction_payload(category_id)
    second_payload["amount"] = "45.25"
    second_payload["description"] = "Bonus"
    client.post("/transactions", json=second_payload)

    response = client.get("/transactions")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["amount"] == "125.50"
    assert data[0]["description"] == "Monthly salary"
    assert data[1]["amount"] == "45.25"
    assert data[1]["description"] == "Bonus"


def test_get_transaction_by_id(client: TestClient) -> None:
    category_id = create_category(client)
    create_response = client.post(
        "/transactions",
        json=transaction_payload(category_id),
    )
    transaction_id = create_response.json()["id"]

    response = client.get(f"/transactions/{transaction_id}")

    assert response.status_code == 200
    assert response.json()["id"] == transaction_id
    assert response.json()["category_id"] == category_id


def test_missing_transaction_returns_404(client: TestClient) -> None:
    response = client.get("/transactions/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Transaction not found"}


def test_partial_update_preserves_omitted_fields(client: TestClient) -> None:
    category_id = create_category(client)
    create_response = client.post(
        "/transactions",
        json=transaction_payload(category_id),
    )
    transaction_id = create_response.json()["id"]

    response = client.patch(
        f"/transactions/{transaction_id}",
        json={"amount": "200.00"},
    )

    assert response.status_code == 200
    assert response.json()["amount"] == "200.00"
    assert response.json()["type"] == "income"
    assert response.json()["description"] == "Monthly salary"


def test_delete_transaction(client: TestClient) -> None:
    category_id = create_category(client)
    create_response = client.post(
        "/transactions",
        json=transaction_payload(category_id),
    )
    transaction_id = create_response.json()["id"]

    response = client.delete(f"/transactions/{transaction_id}")

    assert response.status_code == 204
    assert response.content == b""


def test_deleted_transaction_is_no_longer_returned(client: TestClient) -> None:
    category_id = create_category(client)
    create_response = client.post(
        "/transactions",
        json=transaction_payload(category_id),
    )
    transaction_id = create_response.json()["id"]

    delete_response = client.delete(f"/transactions/{transaction_id}")
    get_response = client.get(f"/transactions/{transaction_id}")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
