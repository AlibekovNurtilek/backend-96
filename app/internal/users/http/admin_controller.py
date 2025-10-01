from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.internal.users.user_service import UserService
from app.domain.schemas import UserCreate, UserResponse, PaginatedUsersResponse
from app.shared.dependencies import get_admin_user


class AdminController:
    def __init__(self):
        pass

    async def create_user(
        self,
        user_data: UserCreate,
        db: Session,
        admin_user=Depends(get_admin_user)
    ) -> UserResponse:
        """Создание пользователя (только для администраторов)"""
        user_service = UserService(db)
        return await user_service.create_user(user_data)

    async def create_admin_user(
        self,
        user_data: UserCreate,
        db: Session,
        admin_user = Depends(get_admin_user)
    ) -> UserResponse:
        """Создание администратора (для первичной настройки)"""
        user_service = UserService(db)
        user_creation_data = UserCreate(
            username=user_data.username,
            password=user_data.password,
            role="admin"
        )
        return await user_service.create_user(user_creation_data)

    async def get_users(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 20,
        admin_user=Depends(get_admin_user)
    ) -> PaginatedUsersResponse:
        """Получение списка пользователей с пагинацией (только для администраторов)"""
        user_service = UserService(db)
        return await user_service.get_users(page=page, page_size=page_size)

    async def delete_user(
        self,
        user_id: int,
        db: Session,
        admin_user=Depends(get_admin_user)
    ) -> dict:
        """Удаление пользователя по id (только для администраторов)"""
        user_service = UserService(db)
        return await user_service.delete_user(user_id)
