from fastapi.testclient import TestClient


def create_category(
    client: TestClient,
    *,
    name: str = "Salary",
    type: str = "income",
) -> int:
    response = client.post(
        "/categories",
        json={"name": name, "type": type},
    )
    return response.json()["id"]


def transaction_payload(
    category_id: int,
    *,
    amount: str = "125.50",
    type: str = "income",
    description: str = "Monthly salary",
    transaction_date: str = "2026-06-24T12:00:00+03:00",
) -> dict[str, str | int]:
    return {
        "category_id": category_id,
        "amount": amount,
        "type": type,
        "description": description,
        "transaction_date": transaction_date,
    }


def create_transaction(
    client: TestClient,
    category_id: int,
    *,
    amount: str = "125.50",
    type: str = "income",
    description: str = "Monthly salary",
    transaction_date: str = "2026-06-24T12:00:00+03:00",
) -> dict[str, str | int]:
    response = client.post(
        "/transactions",
        json=transaction_payload(
            category_id,
            amount=amount,
            type=type,
            description=description,
            transaction_date=transaction_date,
        ),
    )
    return response.json()


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
    create_transaction(
        client,
        category_id,
        amount="125.50",
        description="Monthly salary",
        transaction_date="2026-06-24T12:00:00+03:00",
    )
    create_transaction(
        client,
        category_id,
        amount="45.25",
        description="Bonus",
        transaction_date="2026-06-23T12:00:00+03:00",
    )

    response = client.get("/transactions")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["amount"] == "125.50"
    assert data[0]["description"] == "Monthly salary"
    assert data[1]["amount"] == "45.25"
    assert data[1]["description"] == "Bonus"


def test_transactions_default_list_behavior(client: TestClient) -> None:
    category_id = create_category(client)
    create_transaction(client, category_id, transaction_date="2026-06-20T12:00:00")
    create_transaction(client, category_id, transaction_date="2026-06-22T12:00:00")

    response = client.get("/transactions")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_transactions_limit_and_offset(client: TestClient) -> None:
    category_id = create_category(client)
    create_transaction(
        client,
        category_id,
        amount="10.00",
        transaction_date="2026-06-20T12:00:00",
    )
    create_transaction(
        client,
        category_id,
        amount="20.00",
        transaction_date="2026-06-21T12:00:00",
    )
    create_transaction(
        client,
        category_id,
        amount="30.00",
        transaction_date="2026-06-22T12:00:00",
    )

    response = client.get("/transactions?limit=1&offset=1")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["amount"] == "20.00"


def test_transactions_filter_by_type(client: TestClient) -> None:
    income_category_id = create_category(client, name="Salary", type="income")
    expense_category_id = create_category(client, name="Food", type="expense")
    create_transaction(client, income_category_id, type="income")
    create_transaction(
        client,
        expense_category_id,
        amount="25.00",
        type="expense",
        description="Groceries",
    )

    response = client.get("/transactions?type=expense")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["type"] == "expense"
    assert data[0]["description"] == "Groceries"


def test_transactions_filter_by_category_id(client: TestClient) -> None:
    salary_category_id = create_category(client, name="Salary", type="income")
    bonus_category_id = create_category(client, name="Bonus", type="income")
    create_transaction(client, salary_category_id, description="Salary")
    create_transaction(client, bonus_category_id, description="Bonus")

    response = client.get(f"/transactions?category_id={bonus_category_id}")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["category_id"] == bonus_category_id
    assert data[0]["description"] == "Bonus"


def test_transactions_filter_by_date_from(client: TestClient) -> None:
    category_id = create_category(client)
    create_transaction(
        client,
        category_id,
        description="Before",
        transaction_date="2026-06-20T12:00:00",
    )
    create_transaction(
        client,
        category_id,
        description="After",
        transaction_date="2026-06-22T12:00:00",
    )

    response = client.get("/transactions?date_from=2026-06-21")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "After"


def test_transactions_filter_by_date_to(client: TestClient) -> None:
    category_id = create_category(client)
    create_transaction(
        client,
        category_id,
        description="Before",
        transaction_date="2026-06-20T12:00:00",
    )
    create_transaction(
        client,
        category_id,
        description="After",
        transaction_date="2026-06-22T12:00:00",
    )

    response = client.get("/transactions?date_to=2026-06-21")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["description"] == "Before"


def test_transactions_default_sorting(client: TestClient) -> None:
    category_id = create_category(client)
    create_transaction(
        client,
        category_id,
        description="Old",
        transaction_date="2026-06-20T12:00:00",
    )
    create_transaction(
        client,
        category_id,
        description="New",
        transaction_date="2026-06-22T12:00:00",
    )

    response = client.get("/transactions")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["description"] == "New"
    assert data[1]["description"] == "Old"


def test_transactions_ascending_sorting(client: TestClient) -> None:
    category_id = create_category(client)
    create_transaction(
        client,
        category_id,
        amount="30.00",
        transaction_date="2026-06-20T12:00:00",
    )
    create_transaction(
        client,
        category_id,
        amount="10.00",
        transaction_date="2026-06-22T12:00:00",
    )

    response = client.get("/transactions?sort_by=amount&sort_order=asc")

    assert response.status_code == 200
    data = response.json()
    assert data[0]["amount"] == "10.00"
    assert data[1]["amount"] == "30.00"


def test_transactions_invalid_type_filter_returns_422(client: TestClient) -> None:
    response = client.get("/transactions?type=invalid")

    assert response.status_code == 422


def test_transactions_invalid_sort_by_returns_422(client: TestClient) -> None:
    response = client.get("/transactions?sort_by=id")

    assert response.status_code == 422


def test_transactions_invalid_sort_order_returns_422(client: TestClient) -> None:
    response = client.get("/transactions?sort_order=sideways")

    assert response.status_code == 422


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
