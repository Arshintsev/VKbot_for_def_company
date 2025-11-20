from src.bot.handlers import handle_message
from src.db.database import SessionLocal
from src.db.models import UserSession


class VkMock:
    def __init__(self):
        self.messages = self
        self.sent = []

    def send(self, **kwargs):
        print("DEBUG: VkMock received:", kwargs)
        self.sent.append(kwargs)


def test_category_to_products_flow():
    vk = VkMock()
    user_id = 1001

    handle_message(vk, user_id, "Привет")
    assert "Выберите категорию" in vk.sent[-1]["message"]

    handle_message(vk, user_id, "Хлеб и булки")
    assert "Выберите товар" in vk.sent[-1]["message"]

    with SessionLocal() as session:
        state = session.query(UserSession).filter_by(user_id=user_id).first().state
    assert state == "PRODUCT_SELECTED"


def test_back_from_product_details_returns_to_products():
    vk = VkMock()
    user_id = 2002

    handle_message(vk, user_id, "Привет")
    handle_message(vk, user_id, "Хлеб и булки")
    handle_message(vk, user_id, "Батон")

    assert vk.sent[-1]["message"].startswith("Выберите действие")

    handle_message(vk, user_id, "Назад")
    assert vk.sent[-1]["message"] == "Выберите товар:"

    with SessionLocal() as session:
        state = session.query(UserSession).filter_by(user_id=user_id).first().state
    assert state == "PRODUCT_SELECTED"


def test_back_from_products_shows_categories():
    vk = VkMock()
    user_id = 3005

    handle_message(vk, user_id, "Привет")
    handle_message(vk, user_id, "Хлеб и булки")

    handle_message(vk, user_id, "Назад")

    assert "Выберите категорию" in vk.sent[-1]["message"]


def test_wrong_category_shows_error():
    vk = VkMock()
    user_id = 3003

    handle_message(vk, user_id, "Привет")
    handle_message(vk, user_id, "НЕСУЩЕСТВУЮЩАЯ")

    assert "Категория не найдена" in vk.sent[-1]["message"]
    assert "Хлеб и булки" in vk.sent[-1]["keyboard"]


def test_wrong_product_input():
    vk = VkMock()
    user_id = 3004

    handle_message(vk, user_id, "Привет")
    handle_message(vk, user_id, "Хлеб и булки")
    handle_message(vk, user_id, "НЕСУЩЕСТВУЮЩИЙ_ТОВАР")

    assert "Товар не найден" in vk.sent[-1]["message"]
    assert "Батон" in vk.sent[-1]["keyboard"]
