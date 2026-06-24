# expense-tracker-api
FastAPI backend service for tracking personal income, expenses, categories, and financial summaries.

## Run with Docker

Create a local environment file from the example:

```bash
cp .env.example .env
```

Update the placeholder values in `.env`, then build and start the app with PostgreSQL:

```bash
docker compose up --build
```

The app starts on `http://localhost:8000`. On startup, the app service runs:

```bash
alembic upgrade head
```

Then it starts Uvicorn on `0.0.0.0:8000`.

Check the health endpoint:

```bash
curl http://localhost:8000/health
```

## API

### Health

- `GET /health`

### Categories

- `POST /categories`
- `GET /categories`
- `GET /categories/{category_id}`
- `PATCH /categories/{category_id}`
- `DELETE /categories/{category_id}`

### Transactions

- `POST /transactions`
- `GET /transactions`
- `GET /transactions/summary`
- `GET /transactions/{transaction_id}`
- `PATCH /transactions/{transaction_id}`
- `DELETE /transactions/{transaction_id}`

`GET /transactions` supports `limit`, `offset`, `type`, `category_id`,
`date_from`, `date_to`, `sort_by`, and `sort_order` query parameters.
