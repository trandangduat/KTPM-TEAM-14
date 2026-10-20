from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, model_validator


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
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    original_price: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    flash_sale_price: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)
    stock: int = Field(..., ge=0)
    start_time: datetime | None = None
    end_time: datetime | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_name(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        normalized_name = " ".join(value.split())
        if not normalized_name:
            raise ValueError("Ten san pham khong duoc de trong")
        return normalized_name

    @field_validator("description", mode="before")
    @classmethod
    def normalize_description(cls, value: object) -> object:
        if value is None:
            return None
        if not isinstance(value, str):
            return value
        normalized_description = value.strip()
        return normalized_description or None

    @model_validator(mode="after")
    def validate_price_relationship(self):
        if self.flash_sale_price >= self.original_price:
            raise ValueError("Gia flash sale phai thap hon gia goc")
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValueError("Thoi gian ket thuc phai sau thoi gian bat dau")
        return self


class ProductUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    original_price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    flash_sale_price: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: str | None = None

    @field_validator("name", mode="before")
    @classmethod
    def normalize_optional_name(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
        return " ".join(value.split())

    @field_validator("description", mode="before")
    @classmethod
    def normalize_optional_description(cls, value: object) -> object:
        if value is None or not isinstance(value, str):
            return value
        return value.strip() or None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized_status = value.upper()
        if normalized_status not in {"ACTIVE", "INACTIVE"}:
            raise ValueError("Trang thai san pham khong hop le")
        return normalized_status


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
    sale_state: str
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
