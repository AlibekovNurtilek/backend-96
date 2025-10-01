from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database.config import get_db
from app.internal.users.http.admin_controller import AdminController
from app.domain.schemas import UserCreate, UserResponse, PaginatedUsersResponse
from app.shared.dependencies import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

admin_controller = AdminController()


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Создание пользователя (только для администраторов)"""
    return await admin_controller.create_user(user_data, db, admin_user)


@router.post("/create-admin", response_model=UserResponse)
async def create_admin_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Создание администратора (для первичной настройки)"""
    return await admin_controller.create_admin_user(user_data, db)


@router.get("/users", response_model=PaginatedUsersResponse)
async def get_users(
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Получение списка пользователей с пагинацией (только для администраторов)"""
    return await admin_controller.get_users(db, page=page, page_size=page_size, admin_user=admin_user)


@router.delete("/users/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin_user = Depends(get_admin_user)
):
    """Удаление пользователя по ID (только для администраторов)"""
    return await admin_controller.delete_user(user_id, db, admin_user)
