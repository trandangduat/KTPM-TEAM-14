from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_auth_service, get_current_user
from app.api.schemas import LoginRequest, TokenResponse, UserResponse
from app.domain.models import User
from app.domain.exceptions import UnauthorizedException
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse, summary="Dang nhap")
def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    """Dang nhap he thong va tra ve access token."""
    try:
        token, _ = auth_service.authenticate_user(payload.username, payload.password)
        return TokenResponse(access_token=token)
    except UnauthorizedException as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


@router.post("/logout", summary="Dang xuat")
def logout(current_user: User = Depends(get_current_user)):
    """Dang xuat khoi he thong."""
    return {"message": "Dang xuat thanh cong"}


users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserResponse, summary="Xem thong tin ca nhan")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Xem thong tin chi tiet cua tai khoan dang dang nhap."""
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        created_at=current_user.created_at,
    )
