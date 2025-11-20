import json

from sqlalchemy import (
    DECIMAL,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Category(Base):
    """Модель категории."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    products = relationship(
        "Product", back_populates="category", cascade="all, delete-orphan"
    )


class Product(Base):
    """Модель товара."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    image_url = Column(String)
    price = Column(DECIMAL(8, 2))
    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")
    vk_attachment = Column(String, default=None)  # хранит photo_id


class UserSession(Base):
    """Модель для хранения состояний"""

    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False, unique=True)  # VK ID пользователя
    state = Column(String, nullable=False, default="START")  # Текущее состояние машины
    context = Column(Text, default="{}")  # Дополнительные данные (JSON)
    last_interaction = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def get_context(self) -> dict:
        """Возвращает context как словарь."""
        try:
            return json.loads(self.context)
        except json.JSONDecodeError:
            return {}

    def set_context(self, data: dict):
        """Сохраняет context из словаря."""
        self.context = json.dumps(data)
