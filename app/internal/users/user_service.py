from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.database.models import User
from app.domain.schemas import UserCreate, UserResponse, PageMeta, PaginatedUsersResponse
from app.shared.dependencies import get_password_hash
import math

class UserService:
    def __init__(self, db: Session):
        self.db = db

    async def get_user_by_username(self, username: str) -> User:
        """Получение пользователя по username"""
        user = self.db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Создание нового пользователя"""
        # Проверка существования пользователя
        existing_user = self.db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Создание пользователя
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            username=user_data.username,
            password=hashed_password,
            role=user_data.role
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return UserResponse(**db_user.__dict__)

    async def get_current_user_info(self, user: User) -> UserResponse:
        """Получение информации о текущем пользователе"""
        return UserResponse(**user.__dict__)
    
    async def get_users(
        self, 
        page: int = 1, 
        page_size: int = 20
    ) -> PaginatedUsersResponse:
        """Получение списка пользователей с пагинацией"""
        if page < 1 or page_size < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page and page_size must be positive integers"
            )

        total_items = self.db.query(User).count()
        total_pages = math.ceil(total_items / page_size)
        offset = (page - 1) * page_size

        users = self.db.query(User).offset(offset).limit(page_size).all()

        meta = PageMeta(
            current_page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_items=total_items
        )

        return PaginatedUsersResponse(
            meta=meta,
            items=[UserResponse(**user.__dict__) for user in users]
        )
    
    async def delete_user(self, user_id: int) -> dict:
        """Удаление пользователя по id"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        self.db.delete(user)
        self.db.commit()

        return {"detail": "User deleted successfully"}
