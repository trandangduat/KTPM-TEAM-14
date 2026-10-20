from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_product_service, require_admin
from app.api.schemas import ProductCreateRequest, ProductResponse
from app.domain.models import Product, User
from app.domain.exceptions import NotFoundException, ValidationException
from app.services.product_service import ProductService

router = APIRouter(prefix="/products", tags=["Flash Sale"])


def _to_product_response(product: Product) -> ProductResponse:
    return ProductResponse(
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


@router.get("", response_model=List[ProductResponse], summary="Danh sach san pham Flash Sale")
def list_products(product_service: ProductService = Depends(get_product_service)):
    """Xem danh sach cac san pham dang mo ban flash sale."""
    products = product_service.list_flash_sale_products()
    return [_to_product_response(product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse, summary="Chi tiet san pham Flash Sale")
def get_product(product_id: UUID, product_service: ProductService = Depends(get_product_service)):
    """Xem thong tin chi tiet va so luong ton kho cua mot san pham."""
    try:
        product = product_service.get_product_detail(product_id)
        return _to_product_response(product)
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED, summary="Them san pham Flash Sale")
def create_product(
    payload: ProductCreateRequest,
    product_service: ProductService = Depends(get_product_service),
    current_admin: User = Depends(require_admin),
):
    """Admin them moi mot san pham vao danh sach flash sale."""
    try:
        product = product_service.create_flash_sale_product(
            name=payload.name,
            description=payload.description,
            original_price=payload.original_price,
            flash_sale_price=payload.flash_sale_price,
            stock=payload.stock,
            start_time=payload.start_time,
            end_time=payload.end_time,
        )
        return _to_product_response(product)
    except ValidationException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Xoa san pham Flash Sale")
def delete_product(
    product_id: UUID,
    product_service: ProductService = Depends(get_product_service),
    current_admin: User = Depends(require_admin),
):
    """Admin xoa mot san pham khoi danh sach flash sale."""
    try:
        product_service.delete_flash_sale_product(product_id)
        return None
    except NotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
