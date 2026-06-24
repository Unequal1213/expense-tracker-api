# Expense Tracker API

[![CI](https://github.com/Unequal1213/expense-tracker-api/actions/workflows/ci.yml/badge.svg)](https://github.com/Unequal1213/expense-tracker-api/actions/workflows/ci.yml)

Expense Tracker API is a production-style FastAPI backend for tracking personal
income, expenses, categories, transactions, and financial summaries.

This project is built as a portfolio backend application for a Junior Python
Backend Developer role. It demonstrates REST API design, relational database
modeling, CRUD workflows, filtering, sorting, automated tests, Docker, database
migrations, and GitHub Actions CI.

## Features

- Health check endpoint for service monitoring
- Category CRUD for income and expense categories
- Transaction CRUD linked to existing categories
- Transaction pagination, filtering, and sorting
- Financial summary endpoint with income, expense, balance, counts, and totals by category
- PostgreSQL database support with SQLAlchemy ORM
- Alembic migrations for database schema management
- Docker Compose setup with PostgreSQL
- Pytest test suite using in-memory SQLite for API tests
- Ruff linting
- GitHub Actions CI for automated checks

## Tech Stack

- Python 3.13
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Docker and Docker Compose
- Pytest
- Ruff
- GitHub Actions

## Project Structure

```text
app/
  api/          FastAPI routes and dependencies
  database/     SQLAlchemy database setup
  models/       SQLAlchemy ORM models
  schemas/      Pydantic request and response schemas
  services/     Business logic and database query logic
  main.py       FastAPI application entrypoint
alembic/        Alembic migration environment and migration files
tests/          Pytest test suite
```

The route handlers are intentionally kept thin. Business logic lives in
`app/services/`, while validation and response shapes live in `app/schemas/`.

## Environment Variables

Create a local `.env` file from the example file:

```bash
cp .env.example .env
```

The project expects these variables:

```text
DATABASE_URL=postgresql+psycopg://expense_tracker_user:change_me@postgres:5432/expense_tracker
POSTGRES_USER=expense_tracker_user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=expense_tracker
```

Use placeholder values for local development and replace them with secure values
in real environments. Do not commit `.env` or real secrets.

## Docker Setup

Docker Compose starts both the FastAPI app and PostgreSQL database.

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

The app service waits for PostgreSQL to become healthy, runs:

```bash
alembic upgrade head
```

Then it starts Uvicorn on `0.0.0.0:8000`.

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

## Local Development Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Create a local `.env` file:

```bash
cp .env.example .env
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

For local development without Docker, make sure `DATABASE_URL` points to a
running PostgreSQL database.

## Database Migrations

Apply migrations:

```bash
alembic upgrade head
```

Create a new migration after model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

Check the current migration version:

```bash
alembic current
```

## Tests

Run the test suite:

```bash
python -m pytest
```

Tests use an in-memory SQLite database and FastAPI dependency overrides, so they
do not require a real PostgreSQL database.

## Linting

Run Ruff:

```bash
python -m ruff check .
```

## API Endpoints

### Health

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/health` | Service health check |

### Categories

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/categories` | Create a category |
| GET | `/categories` | List all categories |
| GET | `/categories/{category_id}` | Get a category by ID |
| PATCH | `/categories/{category_id}` | Update a category |
| DELETE | `/categories/{category_id}` | Delete a category |

Allowed category types:

```text
income
expense
```

### Transactions

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/transactions` | Create a transaction linked to a category |
| GET | `/transactions` | List transactions with pagination, filters, and sorting |
| GET | `/transactions/summary` | Get financial summary statistics |
| GET | `/transactions/{transaction_id}` | Get a transaction by ID |
| PATCH | `/transactions/{transaction_id}` | Update a transaction |
| DELETE | `/transactions/{transaction_id}` | Delete a transaction |

Allowed transaction types:

```text
income
expense
```

## Transaction Filtering and Sorting

`GET /transactions` supports these query parameters:

| Parameter | Description |
| --- | --- |
| `limit` | Number of results to return. Default: `20`. Minimum: `1`. Maximum: `100`. |
| `offset` | Number of results to skip. Default: `0`. Minimum: `0`. |
| `type` | Filter by `income` or `expense`. |
| `category_id` | Filter by category ID. |
| `date_from` | Return transactions on or after this date or datetime. |
| `date_to` | Return transactions on or before this date or datetime. |
| `sort_by` | Sort by `transaction_date`, `created_at`, `updated_at`, `amount`, or `type`. |
| `sort_order` | Sort direction: `asc` or `desc`. |

Default sorting is:

```text
transaction_date desc
```

Example:

```bash
curl "http://localhost:8000/transactions?type=expense&limit=10&sort_by=amount&sort_order=desc"
```

## Financial Summary

`GET /transactions/summary` returns portfolio-friendly financial analytics based
on existing transaction records:

```json
{
  "total_income": "1500.00",
  "total_expense": "450.00",
  "balance": "1050.00",
  "income_count": 2,
  "expense_count": 3,
  "totals_by_category": {
    "Salary": "1500.00",
    "Food": "300.00",
    "Transport": "150.00"
  }
}
```

If there are no transactions, totals are `0` and `totals_by_category` is empty.

## Continuous Integration

GitHub Actions runs on every push and pull request.

The CI workflow uses Python 3.13 and runs:

```bash
python -m ruff check .
python -m pytest
```

This helps keep the project linted and tested before changes are merged.
