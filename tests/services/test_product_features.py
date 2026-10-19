from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.api.schemas import ProductCreateRequest
from app.domain.exceptions import ValidationException
from app.domain.models import Product
from app.services.product_service import ProductService


class FakeProductRepository:
    def __init__(self, products=None):
        self.products = products or []
        self.created_product = None

    def get_by_id(self, product_id):
        return next((product for product in self.products if product.id == product_id), None)

    def list_active(self):
        return [product for product in self.products if product.status == "ACTIVE"]

    def create(self, product):
        self.created_product = product
        self.products.append(product)
        return product

    def update_stock(self, product_id, new_stock):
        return None

    def delete(self, product_id):
        return False


def make_product(name, price, stock=5, description=None):
    return Product(
        id=uuid4(),
        name=name,
        description=description,
        original_price=price + Decimal(100),
        flash_sale_price=price,
        stock=stock,
        start_time=None,
        end_time=None,
        status="ACTIVE",
        created_at=datetime.utcnow(),
    )


def valid_product_data(**overrides):
    values = {
        "name": "Ban phim co",
        "description": None,
        "original_price": Decimal(1200000),
        "flash_sale_price": Decimal(900000),
        "stock": 5,
    }
    values.update(overrides)
    return values


def test_create_product_collapses_name_whitespace():
    repository = FakeProductRepository()
    service = ProductService(repository)

    product = service.create_flash_sale_product(
        **valid_product_data(name="  Ban   phim\tco  "),
    )

    assert product.name == "Ban phim co"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("original_price", Decimal("NaN"), "Gia goc khong hop le"),
        ("flash_sale_price", Decimal("Infinity"), "Gia flash sale khong hop le"),
        ("original_price", Decimal("10000000000.00"), "vuot qua gioi han"),
        ("flash_sale_price", Decimal("10.001"), "2 chu so thap phan"),
    ],
)
def test_create_product_rejects_invalid_money(field, value, message):
    service = ProductService(FakeProductRepository())

    with pytest.raises(ValidationException, match=message):
        service.create_flash_sale_product(**valid_product_data(**{field: value}))


@pytest.mark.parametrize("stock", [True, 1.5, "5"])
def test_create_product_requires_integer_stock(stock):
    service = ProductService(FakeProductRepository())

    with pytest.raises(ValidationException, match="phai la so nguyen"):
        service.create_flash_sale_product(**valid_product_data(stock=stock))


def test_schema_rejects_money_with_too_many_decimal_places():
    with pytest.raises(ValidationError):
        ProductCreateRequest(**valid_product_data(flash_sale_price=Decimal("10.001")))


def test_list_products_filters_keyword_case_insensitively():
    keyboard = make_product("Ban phim co", Decimal(900000), description="Gaming RGB")
    mouse = make_product("Chuot khong day", Decimal(500000))
    service = ProductService(FakeProductRepository([keyboard, mouse]))

    assert service.list_flash_sale_products(keyword="  rgb ") == [keyboard]
    assert service.list_flash_sale_products(keyword="CHUOT") == [mouse]


def test_list_products_filters_price_range():
    cheap = make_product("Chuot", Decimal(500000))
    medium = make_product("Ban phim", Decimal(900000))
    expensive = make_product("Man hinh", Decimal(3000000))
    service = ProductService(FakeProductRepository([cheap, medium, expensive]))

    result = service.list_flash_sale_products(
        min_price=Decimal(600000),
        max_price=Decimal(1000000),
    )

    assert result == [medium]


def test_list_products_filters_out_of_stock_products():
    available = make_product("Con hang", Decimal(500000), stock=1)
    sold_out = make_product("Het hang", Decimal(600000), stock=0)
    service = ProductService(FakeProductRepository([available, sold_out]))

    assert service.list_flash_sale_products(in_stock_only=True) == [available]


def test_list_products_rejects_invalid_price_range():
    service = ProductService(FakeProductRepository())

    with pytest.raises(ValidationException, match="toi thieu"):
        service.list_flash_sale_products(
            min_price=Decimal(1000),
            max_price=Decimal(500),
        )


def test_product_reports_sale_state_from_schedule_and_stock():
    now = datetime(2026, 10, 29, 10, 0)
    product = make_product("Ban phim", Decimal(900000))

    product.start_time = now + timedelta(hours=1)
    assert product.sale_state(now) == "UPCOMING"

    product.start_time = now - timedelta(hours=1)
    product.end_time = now + timedelta(hours=1)
    assert product.sale_state(now) == "AVAILABLE"

    product.stock = 0
    assert product.sale_state(now) == "SOLD_OUT"

    product.end_time = now
    assert product.sale_state(now) == "ENDED"


def test_create_product_rejects_invalid_sale_schedule():
    now = datetime(2026, 10, 29, 10, 0)
    service = ProductService(FakeProductRepository())

    with pytest.raises(ValidationException, match="ket thuc"):
        service.create_flash_sale_product(
            **valid_product_data(),
            start_time=now,
            end_time=now - timedelta(minutes=1),
        )


def test_list_products_filters_sale_state():
    now = datetime(2026, 10, 29, 10, 0)
    upcoming = make_product("Sap mo ban", Decimal(500000))
    upcoming.start_time = now + timedelta(hours=1)
    available = make_product("Dang mo ban", Decimal(600000))
    service = ProductService(FakeProductRepository([upcoming, available]))

    assert service.list_flash_sale_products(sale_state="upcoming", at=now) == [upcoming]
    assert service.list_flash_sale_products(sale_state="AVAILABLE", at=now) == [available]


def test_list_products_rejects_unknown_sale_state():
    service = ProductService(FakeProductRepository())

    with pytest.raises(ValidationException, match="Trang thai"):
        service.list_flash_sale_products(sale_state="UNKNOWN")
