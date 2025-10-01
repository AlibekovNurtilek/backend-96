from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database.config import engine, get_db
from app.database.models import Base, User
from app.presentation.api.v1 import auth, admin, tagging
from app.internal.users.http.admin_controller import AdminController
from app.domain.schemas import UserCreate
from app.shared.dependencies import get_password_hash

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FastAPI Backend",
    description="Backend API with clean architecture",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080","http://80.72.180.130:6600" ],  # В продакшене ограничить конкретными доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутов
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(tagging.router)

@app.on_event("startup")
async def startup_event():
    """Создание администратора при первом запуске приложения"""
    db = next(get_db())
    
    # Проверяем, есть ли уже администратор
    admin_user = db.query(User).filter(User.username == "admin").first()
    
    if not admin_user:
        # Создаем администратора
        hashed_password = get_password_hash("admin123")
        db_user = User(
            username="admin",
            password=hashed_password,
            role="admin"
        )
        db.add(db_user)
        db.commit()
        print("Created default admin user: username=admin, role=admin")
        print("Default password: admin123")
    
    db.close()

@app.get("/")
async def root():
    return {"message": "FastAPI Backend is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
