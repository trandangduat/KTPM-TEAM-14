import uuid
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.models import Product
from app.domain.repositories import ProductRepository
from app.domain.exceptions import NotFoundException, ValidationException


class ProductService:

    MONEY_QUANTUM = Decimal("0.01")
    MAX_MONEY_VALUE = Decimal("9999999999.99")

    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    @classmethod
    def _validate_money(cls, value: Decimal, field_name: str) -> None:
        if not isinstance(value, Decimal) or not value.is_finite():
            raise ValidationException(f"{field_name} khong hop le")
        if value <= 0:
            raise ValidationException(f"{field_name} phai lon hon 0")
        if value > cls.MAX_MONEY_VALUE:
            raise ValidationException(f"{field_name} vuot qua gioi han cho phep")
        if value.quantize(cls.MONEY_QUANTUM) != value:
            raise ValidationException(f"{field_name} chi duoc co toi da 2 chu so thap phan")

    @staticmethod
    def _validate_price_filter(
        min_price: Decimal | None,
        max_price: Decimal | None,
    ) -> None:
        for value in (min_price, max_price):
            if value is not None and (
                not isinstance(value, Decimal)
                or not value.is_finite()
                or value < 0
            ):
                raise ValidationException("Khoang gia loc khong hop le")
        if min_price is not None and max_price is not None and min_price > max_price:
            raise ValidationException("Gia toi thieu khong the lon hon gia toi da")

    def list_flash_sale_products(
        self,
        keyword: str | None = None,
        min_price: Decimal | None = None,
        max_price: Decimal | None = None,
        in_stock_only: bool = False,
        sale_state: str | None = None,
        at: datetime | None = None,
    ) -> list[Product]:
        self._validate_price_filter(min_price, max_price)
        allowed_states = {"UPCOMING", "AVAILABLE", "SOLD_OUT", "ENDED", "INACTIVE"}
        normalized_state = sale_state.upper() if sale_state else None
        if normalized_state and normalized_state not in allowed_states:
            raise ValidationException("Trang thai flash sale khong hop le")
        normalized_keyword = keyword.strip().casefold() if keyword else None
        products = self.product_repo.list_active()

        def matches(product: Product) -> bool:
            searchable_text = f"{product.name} {product.description or ''}".casefold()
            return (
                (not normalized_keyword or normalized_keyword in searchable_text)
                and (min_price is None or product.flash_sale_price >= min_price)
                and (max_price is None or product.flash_sale_price <= max_price)
                and (not in_stock_only or product.stock > 0)
                and (not normalized_state or product.sale_state(at) == normalized_state)
            )

        return [product for product in products if matches(product)]

    def get_product_detail(self, product_id: UUID) -> Product:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("San pham khong ton tai")
        return product

    def create_flash_sale_product(
        self,
        name: str,
        description: str | None,
        original_price: Decimal,
        flash_sale_price: Decimal,
        stock: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Product:
        normalized_name = " ".join(name.split())
        normalized_description = description.strip() if description and description.strip() else None

        if not normalized_name:
            raise ValidationException("Ten san pham khong duoc de trong")
        if len(normalized_name) > 200:
            raise ValidationException("Ten san pham khong duoc vuot qua 200 ky tu")
        if not isinstance(stock, int) or isinstance(stock, bool):
            raise ValidationException("So luong ton kho phai la so nguyen")
        if stock < 0:
            raise ValidationException("So luong ton kho khong the am")
        if start_time and end_time and start_time >= end_time:
            raise ValidationException("Thoi gian ket thuc phai sau thoi gian bat dau")
        self._validate_money(original_price, "Gia goc")
        self._validate_money(flash_sale_price, "Gia flash sale")
        if flash_sale_price >= original_price:
            raise ValidationException("Gia flash sale phai thap hon gia goc")

        product = Product(
            id=uuid.uuid4(),
            name=normalized_name,
            description=normalized_description,
            original_price=original_price,
            flash_sale_price=flash_sale_price,
            stock=stock,
            start_time=start_time,
            end_time=end_time,
            status="ACTIVE",
            created_at=datetime.utcnow(),
        )
        return self.product_repo.create(product)

    def delete_flash_sale_product(self, product_id: UUID) -> bool:
        product = self.product_repo.get_by_id(product_id)
        if not product:
            raise NotFoundException("San pham khong ton tai")
        return self.product_repo.delete(product_id)
