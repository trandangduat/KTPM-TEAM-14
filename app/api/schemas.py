from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field


# Schemas cho xac thuc va nguoi dung
class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    username: str
    full_name: str | None = None
    role: str
    created_at: datetime


# Schemas cho san pham
class ProductCreateRequest(BaseModel):
    name: str
    description: str | None = None
    original_price: Decimal = Field(..., gt=0)
    flash_sale_price: Decimal = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    start_time: datetime | None = None
    end_time: datetime | None = None


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    original_price: Decimal
    flash_sale_price: Decimal
    stock: int
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str
    created_at: datetime


# Schemas cho don hang
class OrderCreateRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(..., gt=0)


class OrderResponse(BaseModel):
    id: UUID
    user_id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal
    status: str
    created_at: datetime
