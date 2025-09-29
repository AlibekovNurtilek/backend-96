from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.internal.users.http.admin_controller import AdminController
from app.domain.schemas import UserCreate, UserResponse
from app.shared.dependencies import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])

admin_controller = AdminController()

@router.post("/users", response_model=UserResponse)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db), admin_user = Depends(get_admin_user)):
    """Создание пользователя (только для администраторов)"""
    return await admin_controller.create_user(user_data, db)

@router.post("/create-admin", response_model=UserResponse)
async def create_admin_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Создание администратора (для первичной настройки)"""
    return await admin_controller.create_admin_user(user_data, db)
