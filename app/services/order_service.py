import uuid
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.models import Order
from app.domain.repositories import OrderRepository, ProductRepository
from app.domain.exceptions import NotFoundException, ValidationException, OutOfStockException, ForbiddenException


class OrderService:

    MAX_QUANTITY_PER_ORDER = 20
    MONEY_QUANTUM = Decimal("0.01")

    def __init__(self, order_repo: OrderRepository, product_repo: ProductRepository):
        self.order_repo = order_repo
        self.product_repo = product_repo

    def create_order(self, user_id: UUID, product_id: UUID, quantity: int) -> Order:
        if not isinstance(quantity, int) or isinstance(quantity, bool):
            raise ValidationException("So luong dat mua phai la so nguyen")
        if quantity <= 0:
            raise ValidationException("So luong dat mua phai lon hon 0")
        if quantity > self.MAX_QUANTITY_PER_ORDER:
            raise ValidationException(
                f"Moi don hang chi duoc mua toi da {self.MAX_QUANTITY_PER_ORDER} san pham"
            )

        product = self.product_repo.get_by_id(product_id)
        if not product or product.status != "ACTIVE":
            raise NotFoundException("San pham khong ton tai hoac da ngung ban")

        sale_state = product.sale_state()
        if sale_state == "UPCOMING":
            raise ValidationException("Chuong trinh flash sale chua bat dau")
        if sale_state == "ENDED":
            raise ValidationException("Chuong trinh flash sale da ket thuc")
        if sale_state == "SOLD_OUT":
            raise OutOfStockException("San pham da het hang")

        # Kiem tra so luong ton kho
        if product.stock < quantity:
            raise OutOfStockException("San pham khong du so luong ton kho")

        # Tru ton kho truc tiep trong co so du lieu
        new_stock = product.stock - quantity
        self.product_repo.update_stock(product.id, new_stock)

        # Tao don hang moi
        unit_price = product.flash_sale_price
        total_price = (unit_price * Decimal(quantity)).quantize(self.MONEY_QUANTUM)

        order = Order(
            id=uuid.uuid4(),
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
            total_price=total_price,
            status="PENDING",
            created_at=datetime.utcnow(),
        )
        return self.order_repo.create(order)

    def list_user_orders(self, user_id: UUID) -> list[Order]:
        return self.order_repo.list_by_user_id(user_id)

    def get_order_detail(self, order_id: UUID, user_id: UUID) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Don hang khong ton tai")
        if order.user_id != user_id:
            raise ForbiddenException("Khong co quyen truy cap don hang nay")
        return order

    def cancel_order(self, order_id: UUID, user_id: UUID) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise NotFoundException("Don hang khong ton tai")
        if order.user_id != user_id:
            raise ForbiddenException("Khong co quyen huy don hang nay")
        if order.status == "CANCELLED":
            raise ValidationException("Don hang da bi huy truoc do")

        # Hoan lai so luong vao kho
        product = self.product_repo.get_by_id(order.product_id)
        if product:
            self.product_repo.update_stock(product.id, product.stock + order.quantity)

        updated_order = self.order_repo.update_status(order_id, "CANCELLED")
        return updated_order
