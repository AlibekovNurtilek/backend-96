from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import timedelta
from app.database.models import User
from app.domain.schemas import UserLogin, Token
from app.shared.dependencies import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    async def authenticate_user(self, user_data: UserLogin) -> Token:
        """Аутентификация пользователя"""
        user = self.db.query(User).filter(User.username == user_data.username).first()
        
        if not user or not verify_password(user_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inactive user"
            )

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
