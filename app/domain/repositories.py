from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.models import User, Product, Order


class UserRepository(ABC):

    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        pass

    @abstractmethod
    def create(self, user: User) -> User:
        pass


class ProductRepository(ABC):

    @abstractmethod
    def get_by_id(self, product_id: UUID) -> Product | None:
        pass

    @abstractmethod
    def list_active(self) -> list[Product]:
        pass

    @abstractmethod
    def create(self, product: Product) -> Product:
        pass

    @abstractmethod
    def update(self, product: Product) -> Product:
        pass

    @abstractmethod
    def update_stock(self, product_id: UUID, new_stock: int) -> Product | None:
        pass

    @abstractmethod
    def delete(self, product_id: UUID) -> bool:
        pass


class OrderRepository(ABC):

    @abstractmethod
    def get_by_id(self, order_id: UUID) -> Order | None:
        pass

    @abstractmethod
    def list_by_user_id(self, user_id: UUID) -> list[Order]:
        pass

    @abstractmethod
    def create(self, order: Order) -> Order:
        pass

    @abstractmethod
    def update_status(self, order_id: UUID, status: str) -> Order | None:
        pass
