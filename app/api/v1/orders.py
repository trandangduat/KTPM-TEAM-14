from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.api.dependencies import get_order_service, get_current_user
from app.api.schemas import OrderCreateRequest, OrderResponse, OrderSummaryResponse
from app.domain.exceptions import (
    NotFoundException,
    ValidationException,
    OutOfStockException,
    ForbiddenException,
)
from app.services.order_service import OrderService

# Toan bo router yeu cau xac thuc: get_current_user chay mot lan o cap router
# va gan nguoi dung vao request.state.user.
router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    dependencies=[Depends(get_current_user)],
)


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED, summary="Dat mua san pham Flash Sale")
def create_order(
    request: Request,
    payload: OrderCreateRequest,
    order_service: OrderService = Depends(get_order_service),
):
    """Khach hang dat mua san pham flash sale."""
    try:
        order = order_service.create_order(
            user_id=request.state.user.id,
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


@router.get("", response_model=list[OrderResponse], summary="Danh sach don hang")
def list_orders(
    request: Request,
    order_status: str | None = Query(default=None, alias="status"),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    order_service: OrderService = Depends(get_order_service),
):
    """Xem danh sach don hang cua nguoi dung dang dang nhap."""
    try:
        orders = order_service.list_user_orders(
            request.state.user.id,
            order_status=order_status,
            offset=offset,
            limit=limit,
        )
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
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


@router.get("/summary", response_model=OrderSummaryResponse, summary="Thong ke don hang")
def get_order_summary(
    request: Request,
    order_service: OrderService = Depends(get_order_service),
):
    """Tong hop so don hang va tong chi tieu cua nguoi dung."""
    return OrderSummaryResponse(**order_service.get_user_order_summary(request.state.user.id))


@router.get("/{order_id}", response_model=OrderResponse, summary="Chi tiet don hang")
def get_order(
    request: Request,
    order_id: UUID,
    order_service: OrderService = Depends(get_order_service),
):
    """Xem chi tiet mot don hang cu the."""
    try:
        order = order_service.get_order_detail(order_id, request.state.user.id)
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


@router.post("/{order_id}/cancel", response_model=OrderResponse, summary="Huy don hang")
def cancel_order(
    request: Request,
    order_id: UUID,
    order_service: OrderService = Depends(get_order_service),
):
    """Huy don hang va hoan lai so luong vao ton kho."""
    try:
        order = order_service.cancel_order(order_id, request.state.user.id)
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
