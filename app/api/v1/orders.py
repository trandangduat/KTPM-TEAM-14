from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_order_service, get_current_user
from app.api.schemas import OrderCreateRequest, OrderResponse
from app.domain.models import User
from app.domain.exceptions import (
    NotFoundException,
    ValidationException,
    OutOfStockException,
    ForbiddenException,
)
from app.services.order_service import OrderService

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Dat mua san pham Flash Sale")
def create_order(
    payload: OrderCreateRequest,
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    """Khach hang dat mua san pham flash sale."""
    try:
        order = order_service.create_order(
            user_id=current_user.id,
            product_id=payload.product_id,
            quantity=payload.quantity,
        )
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
        )
    except OutOfStockException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except (NotFoundException, ValidationException) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/me", response_model=List[OrderResponse], summary="Lich su don hang cua toi")
def list_my_orders(
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    """Xem danh sach don hang cua nguoi dung dang dang nhap."""
    orders = order_service.list_user_orders(current_user.id)
    return [
        OrderResponse(
            id=o.id,
            user_id=o.user_id,
            product_id=o.product_id,
            quantity=o.quantity,
            unit_price=o.unit_price,
            total_price=o.total_price,
            status=o.status,
            created_at=o.created_at,
        )
        for o in orders
    ]


@router.get("/{order_id}", response_model=OrderResponse, summary="Chi tiet don hang")
def get_order(
    order_id: UUID,
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    """Xem chi tiet mot don hang cu the."""
    try:
        order = order_service.get_order_detail(order_id, current_user.id)
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
        )
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ForbiddenException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))


@router.delete("/{order_id}", response_model=OrderResponse, summary="Huy don hang")
def cancel_order(
    order_id: UUID,
    order_service: OrderService = Depends(get_order_service),
    current_user: User = Depends(get_current_user),
):
    """Huy don hang va hoan lai so luong vao ton kho."""
    try:
        order = order_service.cancel_order(order_id, current_user.id)
        return OrderResponse(
            id=order.id,
            user_id=order.user_id,
            product_id=order.product_id,
            quantity=order.quantity,
            unit_price=order.unit_price,
            total_price=order.total_price,
            status=order.status,
            created_at=order.created_at,
        )
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ForbiddenException as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
