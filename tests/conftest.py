import os
import sys
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DATABASE_URL", "sqlite:///test_vk_bot.db")

from src.db.database import SessionLocal, engine  # noqa: E402
from src.db.models import Base, Category, Product  # noqa: E402


def _seed_data():
    session = SessionLocal()
    categories = [
        Category(name="Хлеб и булки"),
        Category(name="Сладкая выпечка"),
        Category(name="Печенье и пряники"),
    ]
    session.add_all(categories)
    session.flush()

    products = [
        Product(
            name="Батон",
            description="Свежий пшеничный батон",
            price=100.0,
            category_id=categories[0].id,
        ),
        Product(
            name="Багет",
            description="Французский багет",
            price=120.0,
            category_id=categories[0].id,
        ),
        Product(
            name="Круассан",
            description="Сливочный круассан",
            price=90.0,
            category_id=categories[1].id,
        ),
    ]
    session.add_all(products)
    session.commit()
    session.close()


@pytest.fixture(autouse=True)
def fresh_database(tmp_path):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    _seed_data()
    yield
    Base.metadata.drop_all(bind=engine)
