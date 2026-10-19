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

    def sale_state(self, at: datetime | None = None) -> str:
        current_time = at or datetime.utcnow()
        if self.status != "ACTIVE":
            return "INACTIVE"
        if self.start_time and current_time < self.start_time:
            return "UPCOMING"
        if self.end_time and current_time >= self.end_time:
            return "ENDED"
        if self.stock <= 0:
            return "SOLD_OUT"
        return "AVAILABLE"


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
