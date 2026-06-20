# AGENTS.md

## Project context

This is a portfolio backend project for a self-taught Junior Python Backend Developer.

Project name:
Expense Tracker API

Main goal:
Build a production-style FastAPI backend for tracking personal income, expenses, categories, transactions, and financial summaries.

The project should demonstrate:
- backend API design
- database modeling
- relational data
- CRUD workflows
- filtering and sorting
- financial summary/statistics endpoint
- testing
- Docker
- GitHub Actions CI

## Tech stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Docker
- Pytest
- Ruff
- GitHub Actions

## Development rules

- Do not rewrite the entire project unless explicitly requested.
- Make small, focused changes.
- Explain every changed file.
- Preserve a clean FastAPI project structure.
- Use type hints.
- Follow PEP8.
- Avoid quick hacks.
- Do not commit secrets.
- Do not hardcode API keys, passwords, tokens, or database URLs.
- Use environment variables for configuration.
- Keep business logic separate from API routes.
- Prefer maintainable code over clever code.

## Initial MVP

Build a backend API for tracking personal finances.

Core resources:
- Category
- Transaction

Category fields:
- id
- name
- type
- created_at
- updated_at

Transaction fields:
- id
- category_id
- amount
- type
- description
- transaction_date
- created_at
- updated_at

Allowed category/transaction types:
- income
- expense

Initial endpoints:
- GET /health
- POST /categories
- GET /categories
- GET /categories/{category_id}
- PATCH /categories/{category_id}
- DELETE /categories/{category_id}
- POST /transactions
- GET /transactions
- GET /transactions/{transaction_id}
- PATCH /transactions/{transaction_id}
- DELETE /transactions/{transaction_id}
- GET /transactions/summary

Summary endpoint should return:
- total_income
- total_expense
- balance
- counts by type
- totals by category

## Review guidelines

- Check for security issues.
- Check for hardcoded secrets.
- Check database session handling.
- Check API validation.
- Check test coverage.
- Check whether the code is understandable for a Junior Developer.
