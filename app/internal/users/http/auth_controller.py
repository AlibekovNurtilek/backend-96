from fastapi import Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database.config import get_db
from app.internal.auth.auth_service import AuthService
from app.domain.schemas import UserLogin, Token
from app.shared.dependencies import get_current_user
from app.database.models import User

class AuthController:
    def __init__(self):
        pass

    async def login(self, user_data: UserLogin, response:Response, db: Session = Depends(get_db)) -> Token:
        """Вход в систему"""
        auth_service = AuthService(db)
        token = await auth_service.authenticate_user(user_data)
        
        # Устанавливаем токен в httpOnly cookie
        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            secure=False,  # В продакшене должно быть True для HTTPS
            samesite="lax"
        )
        
        return token

    async def logout(self, response: Response):
        """Выход из системы"""
        response.delete_cookie(key="access_token")
        return {"message": "Successfully logged out"}

    async def me(self, current_user: User = Depends(get_current_user)):
        """Получение информации о текущем пользователе"""
        from app.internal.users.user_service import UserService
        return await UserService(None).get_current_user_info(current_user)
