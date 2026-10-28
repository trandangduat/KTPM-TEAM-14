from uuid import UUID
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.domain.exceptions import NotFoundException
from app.domain.models import User
from app.domain.repositories import UserRepository, ProductRepository, OrderRepository
from app.infrastructure.repositories import (
    SqlAlchemyUserRepository,
    SqlAlchemyProductRepository,
    SqlAlchemyOrderRepository,
)
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.order_service import OrderService

security_scheme = HTTPBearer(auto_error=False)


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return SqlAlchemyUserRepository(db)


def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    return SqlAlchemyProductRepository(db)


def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return SqlAlchemyOrderRepository(db)


def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo)


def get_product_service(product_repo: ProductRepository = Depends(get_product_repository)) -> ProductService:
    return ProductService(product_repo)


def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    product_repo: ProductRepository = Depends(get_product_repository),
) -> OrderService:
    return OrderService(order_repo, product_repo)


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Xac thuc token va gan nguoi dung vao request.state.user.

    Duoc gan o cap router (APIRouter(dependencies=[...])) nen cac endpoint
    khong phai khai bao lai; endpoint doc nguoi dung qua request.state.user.
    """
    if not credentials:
        raise _unauthorized("Thieu token xac thuc")

    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise _unauthorized("Token khong hop le hoac da het han")

    # Chi bat loi lien quan den token/nguoi dung. Loi CSDL (nghen pool,
    # mat ket noi...) duoc de lot ra thanh 5xx, khong bi bien thanh 401.
    try:
        user_id = UUID(payload["sub"])
        user = auth_service.get_current_user_profile(user_id)
    except (ValueError, TypeError, NotFoundException):
        raise _unauthorized("Khong the xac thuc nguoi dung")

    request.state.user = user
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Chi quan tri vien moi co quyen thuc hien thao tac nay",
        )
    return current_user
