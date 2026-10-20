from uuid import UUID
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.exceptions import ConflictException
from app.domain.models import User, Product, Order
from app.domain.repositories import UserRepository, ProductRepository, OrderRepository
from app.infrastructure.models import UserModel, ProductModel, OrderModel


class SqlAlchemyUserRepository(UserRepository):

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            password_hash=model.password_hash,
            full_name=model.full_name,
            role=model.role,
            created_at=model.created_at,
        )

    def get_by_id(self, user_id: UUID) -> User | None:
        model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_entity(model) if model else None

    def get_by_username(self, username: str) -> User | None:
        model = self.db.query(UserModel).filter(UserModel.username == username).first()
        return self._to_entity(model) if model else None

    def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            username=user.username,
            password_hash=user.password_hash,
            full_name=user.full_name,
            role=user.role,
            created_at=user.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)


class SqlAlchemyProductRepository(ProductRepository):

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: ProductModel) -> Product:
        return Product(
            id=model.id,
            name=model.name,
            description=model.description,
            original_price=model.original_price,
            flash_sale_price=model.flash_sale_price,
            stock=model.stock,
            start_time=model.start_time,
            end_time=model.end_time,
            status=model.status,
            created_at=model.created_at,
        )

    def get_by_id(self, product_id: UUID) -> Product | None:
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        return self._to_entity(model) if model else None

    def list_active(self) -> list[Product]:
        models = self.db.query(ProductModel).filter(ProductModel.status == "ACTIVE").all()
        return [self._to_entity(m) for m in models]

    def create(self, product: Product) -> Product:
        model = ProductModel(
            id=product.id,
            name=product.name,
            description=product.description,
            original_price=product.original_price,
            flash_sale_price=product.flash_sale_price,
            stock=product.stock,
            start_time=product.start_time,
            end_time=product.end_time,
            status=product.status,
            created_at=product.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update(self, product: Product) -> Product:
        model = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
        if not model:
            raise ConflictException("San pham khong con ton tai de cap nhat")
        model.name = product.name
        model.description = product.description
        model.original_price = product.original_price
        model.flash_sale_price = product.flash_sale_price
        model.stock = product.stock
        model.start_time = product.start_time
        model.end_time = product.end_time
        model.status = product.status
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update_stock(self, product_id: UUID, new_stock: int) -> Product | None:
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            return None
        model.stock = new_stock
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def delete(self, product_id: UUID) -> bool:
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if not model:
            return False
        self.db.delete(model)
        try:
            self.db.commit()
        except IntegrityError:
            # San pham da co don hang tham chieu (khoa ngoai orders.product_id)
            self.db.rollback()
            raise ConflictException("San pham da co don hang, khong the xoa")
        return True


class SqlAlchemyOrderRepository(OrderRepository):

    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            product_id=model.product_id,
            quantity=model.quantity,
            unit_price=model.unit_price,
            total_price=model.total_price,
            status=model.status,
            created_at=model.created_at,
        )

    def get_by_id(self, order_id: UUID) -> Order | None:
        model = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        return self._to_entity(model) if model else None

    def list_by_user_id(self, user_id: UUID) -> list[Order]:
        models = self.db.query(OrderModel).filter(OrderModel.user_id == user_id).order_by(OrderModel.created_at.desc()).all()
        return [self._to_entity(m) for m in models]

    def create(self, order: Order) -> Order:
        model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)

    def update_status(self, order_id: UUID, status: str) -> Order | None:
        model = self.db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not model:
            return None
        model.status = status
        self.db.commit()
        self.db.refresh(model)
        return self._to_entity(model)
