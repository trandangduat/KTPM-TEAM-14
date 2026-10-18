from decimal import Decimal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.dependencies import get_product_service, require_admin
from app.api.schemas import ProductCreateRequest, ProductResponse
from app.domain.exceptions import ConflictException, NotFoundException, ValidationException
from app.services.product_service import ProductService

# Route cong khai: xem san pham
router = APIRouter(prefix="/products", tags=["Flash Sale"])

# Route quan tri: require_admin (gom ca xac thuc) gan o cap router
admin_router = APIRouter(
    prefix="/products",
    tags=["Flash Sale"],
    dependencies=[Depends(require_admin)],
)


@router.get("", response_model=list[ProductResponse], summary="Danh sach san pham Flash Sale")
def list_products(
    keyword: str | None = Query(default=None, max_length=100),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    in_stock_only: bool = Query(default=False),
    product_service: ProductService = Depends(get_product_service),
):
    """Xem danh sach cac san pham dang mo ban flash sale."""
    try:
        products = product_service.list_flash_sale_products(
            keyword=keyword,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
        )
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return [
        ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            original_price=p.original_price,
            flash_sale_price=p.flash_sale_price,
            stock=p.stock,
            start_time=p.start_time,
            end_time=p.end_time,
            status=p.status,
            created_at=p.created_at,
        )
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductResponse, summary="Chi tiet san pham Flash Sale")
def get_product(product_id: UUID, product_service: ProductService = Depends(get_product_service)):
    """Xem thong tin chi tiet va so luong ton kho cua mot san pham."""
    try:
        p = product_service.get_product_detail(product_id)
        return ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            original_price=p.original_price,
            flash_sale_price=p.flash_sale_price,
            stock=p.stock,
            start_time=p.start_time,
            end_time=p.end_time,
            status=p.status,
            created_at=p.created_at,
        )
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@admin_router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Them san pham Flash Sale")
def create_product(
    payload: ProductCreateRequest,
    product_service: ProductService = Depends(get_product_service),
):
    """Admin them moi mot san pham vao danh sach flash sale."""
    try:
        p = product_service.create_flash_sale_product(
            name=payload.name,
            description=payload.description,
            original_price=payload.original_price,
            flash_sale_price=payload.flash_sale_price,
            stock=payload.stock,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
        return ProductResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            original_price=p.original_price,
            flash_sale_price=p.flash_sale_price,
            stock=p.stock,
            start_time=p.start_time,
            end_time=p.end_time,
            status=p.status,
            created_at=p.created_at,
        )
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@admin_router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xoa san pham Flash Sale")
def delete_product(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service),
):
    """Admin xoa mot san pham khoi danh sach flash sale."""
    try:
        product_service.delete_flash_sale_product(product_id)
        return
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except ConflictException as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
