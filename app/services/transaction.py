from datetime import date, datetime, time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.transaction import (
    TransactionCreate,
    TransactionSortBy,
    TransactionSortOrder,
    TransactionType,
    TransactionUpdate,
)


def create_transaction(
    db: Session,
    transaction_data: TransactionCreate,
) -> Transaction | None:
    if db.get(Category, transaction_data.category_id) is None:
        return None

    transaction = Transaction(**transaction_data.model_dump())

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


def list_transactions(
    db: Session,
    *,
    limit: int = 20,
    offset: int = 0,
    transaction_type: TransactionType | None = None,
    category_id: int | None = None,
    date_from: date | datetime | None = None,
    date_to: date | datetime | None = None,
    sort_by: TransactionSortBy = "transaction_date",
    sort_order: TransactionSortOrder = "desc",
) -> list[Transaction]:
    statement = select(Transaction)

    if transaction_type is not None:
        statement = statement.where(Transaction.type == transaction_type)

    if category_id is not None:
        statement = statement.where(Transaction.category_id == category_id)

    if date_from is not None:
        statement = statement.where(
            Transaction.transaction_date >= normalize_start_datetime(date_from)
        )

    if date_to is not None:
        statement = statement.where(
            Transaction.transaction_date <= normalize_end_datetime(date_to)
        )

    sort_column = getattr(Transaction, sort_by)
    if sort_order == "desc":
        sort_column = sort_column.desc()

    statement = statement.order_by(sort_column).offset(offset).limit(limit)
    transactions = db.scalars(statement).all()
    return list(transactions)


def normalize_start_datetime(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value

    return datetime.combine(value, time.min)


def normalize_end_datetime(value: date | datetime) -> datetime:
    if isinstance(value, datetime):
        return value

    return datetime.combine(value, time.max)


def get_transaction(db: Session, transaction_id: int) -> Transaction | None:
    return db.get(Transaction, transaction_id)


def update_transaction(
    db: Session,
    transaction: Transaction,
    transaction_data: TransactionUpdate,
) -> Transaction | None:
    update_data = transaction_data.model_dump(exclude_unset=True)

    category_id = update_data.get("category_id")
    if category_id is not None and db.get(Category, category_id) is None:
        return None

    for field, value in update_data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)

    return transaction


def delete_transaction(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()
