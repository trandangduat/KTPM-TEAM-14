from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class User:
    id: UUID
    username: str
    password_hash: str
    full_name: str | None
    role: str
    created_at: datetime


@dataclass
class Product:
    id: UUID
    name: str
    description: str | None
    original_price: Decimal
    flash_sale_price: Decimal
    stock: int
    start_time: datetime | None
    end_time: datetime | None
    status: str
    created_at: datetime


@dataclass
class Order:
    id: UUID
    user_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    status: str
    created_at: datetime
