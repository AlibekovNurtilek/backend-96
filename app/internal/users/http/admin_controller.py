from fastapi import Depends
from sqlalchemy.orm import Session
from app.internal.users.user_service import UserService
from app.domain.schemas import UserCreate, UserResponse
from app.shared.dependencies import get_admin_user

class AdminController:
    def __init__(self):
        pass

    async def create_user(self, user_data: UserCreate, db: Session, admin_user = None) -> UserResponse:
        """Создание пользователя (только для администраторов)"""
        user_service = UserService(db)
        return await user_service.create_user(user_data)

    async def create_admin_user(self, user_data: UserCreate, db: Session) -> UserResponse:
        """Создание администратора (для первичной настройки)"""
        user_service = UserService(db)
        # Принудительно устанавливаем роль admin
        user_creation_data = UserCreate(
            username=user_data.username,
            password=user_data.password,
            role="admin"
        )
        return await user_service.create_user(user_creation_data)
