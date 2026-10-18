from typing import Tuple
from uuid import UUID

from app.domain.models import User
from app.domain.repositories import UserRepository
from app.domain.exceptions import UnauthorizedException, NotFoundException
from app.core.security import verify_password, create_access_token


class AuthService:

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate_user(self, username: str, password: str) -> Tuple[str, User]:
        user = self.user_repo.get_by_username(username)
        if not user:
            raise UnauthorizedException("Sai ten dang nhap hoac mat khau")

        if not verify_password(password, user.password_hash):
            raise UnauthorizedException("Sai ten dang nhap hoac mat khau")

        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role}
        )
        return access_token, user

    def get_current_user_profile(self, user_id: UUID) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundException("Nguoi dung khong ton tai")
        return user
