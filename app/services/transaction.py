from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionCreate, TransactionUpdate


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


def list_transactions(db: Session) -> list[Transaction]:
    transactions = db.scalars(select(Transaction).order_by(Transaction.id)).all()
    return list(transactions)


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
