from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.internal.users.http.auth_controller import AuthController
from app.domain.schemas import UserLogin, Token, UserResponse
from app.shared.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["authentication"])

auth_controller = AuthController()

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, response: Response, db: Session = Depends(get_db)):
    """Вход в систему"""
    return await auth_controller.login(user_data, response, db)

@router.post("/logout")
async def logout(response: Response):
    """Выход из системы"""
    return await auth_controller.logout(response)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return await auth_controller.me(current_user)
