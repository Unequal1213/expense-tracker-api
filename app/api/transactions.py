from datetime import date, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.schemas.transaction import (
    TransactionCreate,
    TransactionResponse,
    TransactionSortBy,
    TransactionSortOrder,
    TransactionSummaryResponse,
    TransactionType,
    TransactionUpdate,
)
from app.services import transaction as transaction_service

router = APIRouter(prefix="/transactions", tags=["transactions"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post(
    "",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: DbSession,
) -> TransactionResponse:
    transaction = transaction_service.create_transaction(db, transaction_data)

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return transaction


@router.get("", response_model=list[TransactionResponse])
def list_transactions(
    db: DbSession,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    type: TransactionType | None = None,
    category_id: int | None = None,
    date_from: date | datetime | None = None,
    date_to: date | datetime | None = None,
    sort_by: TransactionSortBy = "transaction_date",
    sort_order: TransactionSortOrder = "desc",
) -> list[TransactionResponse]:
    return transaction_service.list_transactions(
        db,
        limit=limit,
        offset=offset,
        transaction_type=type,
        category_id=category_id,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
    )


@router.get("/summary", response_model=TransactionSummaryResponse)
def get_transaction_summary(db: DbSession) -> TransactionSummaryResponse:
    return transaction_service.get_transaction_summary(db)


@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: DbSession,
) -> TransactionResponse:
    transaction = transaction_service.get_transaction(db, transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return transaction


@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: DbSession,
) -> TransactionResponse:
    transaction = transaction_service.get_transaction(db, transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    updated_transaction = transaction_service.update_transaction(
        db,
        transaction,
        transaction_data,
    )

    if updated_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    return updated_transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: DbSession,
) -> Response:
    transaction = transaction_service.get_transaction(db, transaction_id)

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    transaction_service.delete_transaction(db, transaction)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
