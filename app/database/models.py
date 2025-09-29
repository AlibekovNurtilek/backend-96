from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.types import JSON
from .config import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="annotator")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Sentence(Base):
    __tablename__ = 'sentences'

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True)  # Текст предложения
    is_corrected = Column(Integer, default=0)  # 0 - не исправлено, 1 - исправлено
    
    tokens = relationship("Token", back_populates="sentence")

class Token(Base):
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    # Новое поле для хранения индекса токена в предложении, поддерживает диапазоны
    token_index = Column(String, index=True)  # Индекс токена в предложении (например, "3-5" или "1")
    form = Column(String, index=True)  # Форма токена (например, слово)
    lemma = Column(String)  # Лемма токена
    pos = Column(String)  # Часть речи
    xpos = Column(String)  # Точная часть речи
    feats = Column(JSON)  # Характеристики токена (например, морфологические признаки)
    sentence_id = Column(Integer, ForeignKey("sentences.id"))
    sentence = relationship("Sentence", back_populates="tokens")
    