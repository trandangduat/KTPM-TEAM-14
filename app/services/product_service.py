import uuid
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.models import Product
from app.domain.repositories import ProductRepository
from app.domain.exceptions import NotFoundException, ValidationException


class ProductService:

    def __init__(self, product_repo: ProductRepository):
        self.product_repo = product_repo

    def list_flash_sale_products(self) -> list[Product]:
        return self.product_repo.list_active()

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
        if stock < 0:
            raise ValidationException("So luong ton kho khong the am")
        if flash_sale_price < 0 or original_price < 0:
            raise ValidationException("Gia san pham khong hop le")

        product = Product(
            id=uuid.uuid4(),
            name=name,
            description=description,
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
