from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

TransactionType = Literal["income", "expense"]


class TransactionCreate(BaseModel):
    category_id: int
    amount: Decimal = Field(gt=0)
    type: TransactionType
    description: str | None = Field(default=None, max_length=255)
    transaction_date: datetime


class TransactionUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    type: TransactionType | None = None
    description: str | None = Field(default=None, max_length=255)
    transaction_date: datetime | None = None


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    amount: Decimal
    type: TransactionType
    description: str | None
    transaction_date: datetime
    created_at: datetime
    updated_at: datetime
