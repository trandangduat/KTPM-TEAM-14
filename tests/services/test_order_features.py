from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

import pytest

from app.domain.exceptions import OutOfStockException, ValidationException
from app.domain.models import Product
from app.services.order_service import OrderService


class FakeProductRepository:
    def __init__(self, product):
        self.product = product

    def get_by_id(self, product_id):
        return self.product if self.product.id == product_id else None

    def update_stock(self, product_id, new_stock):
        if self.product.id != product_id:
            return None
        self.product.stock = new_stock
        return self.product


class FakeOrderRepository:
    def __init__(self):
        self.orders = []

    def create(self, order):
        self.orders.append(order)
        return order

    def get_by_id(self, order_id):
        return next((order for order in self.orders if order.id == order_id), None)

    def list_by_user_id(self, user_id):
        return [order for order in self.orders if order.user_id == user_id]

    def update_status(self, order_id, status):
        order = self.get_by_id(order_id)
        if order:
            order.status = status
        return order


def make_product(**overrides):
    values = {
        "id": uuid4(),
        "name": "Ban phim co",
        "description": None,
        "original_price": Decimal("1200000.00"),
        "flash_sale_price": Decimal("899999.99"),
        "stock": 30,
        "start_time": None,
        "end_time": None,
        "status": "ACTIVE",
        "created_at": datetime.utcnow(),
    }
    values.update(overrides)
    return Product(**values)


def make_service(product):
    return OrderService(FakeOrderRepository(), FakeProductRepository(product))


def test_create_order_calculates_total_and_reduces_stock():
    product = make_product(stock=10)
    service = make_service(product)

    order = service.create_order(uuid4(), product.id, 3)

    assert order.unit_price == Decimal("899999.99")
    assert order.total_price == Decimal("2699999.97")
    assert product.stock == 7


@pytest.mark.parametrize("quantity", [0, -1, True, Decimal("1.5")])
def test_create_order_rejects_invalid_quantity(quantity):
    product = make_product()
    service = make_service(product)

    with pytest.raises(ValidationException):
        service.create_order(uuid4(), product.id, quantity)


def test_create_order_enforces_quantity_limit():
    product = make_product(stock=100)
    service = make_service(product)

    with pytest.raises(ValidationException, match="toi da 20"):
        service.create_order(uuid4(), product.id, 21)


@pytest.mark.parametrize(
    ("start_delta", "end_delta", "message"),
    [
        (timedelta(minutes=5), timedelta(hours=1), "chua bat dau"),
        (timedelta(hours=-2), timedelta(minutes=-1), "da ket thuc"),
    ],
)
def test_create_order_requires_open_sale_window(start_delta, end_delta, message):
    now = datetime.utcnow()
    product = make_product(start_time=now + start_delta, end_time=now + end_delta)
    service = make_service(product)

    with pytest.raises(ValidationException, match=message):
        service.create_order(uuid4(), product.id, 1)


def test_create_order_reports_sold_out_product():
    product = make_product(stock=0)
    service = make_service(product)

    with pytest.raises(OutOfStockException, match="het hang"):
        service.create_order(uuid4(), product.id, 1)
