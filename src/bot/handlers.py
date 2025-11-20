import random
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from src.db.database import SessionLocal
from src.db.models import Category, Product
from src.bot.states import UserBot
from src.bot.keyboards import main_menu_keyboard
from typing import List, Optional


def _normalize_text(value: Optional[str]) -> str:
    """Возвращает строку для сравнения кнопок."""
    return (value or "").strip().lower()


def _find_by_name(items: List, text: str):
    """Ищет объект по имени без учета регистра и пробелов."""
    normalized = _normalize_text(text)
    if not normalized:
        return None
    for item in items:
        if _normalize_text(item.name) == normalized:
            return item
    return None


def get_categories(session) -> List[Category]:
    """Возвращает все категории из базы."""
    return session.query(Category).all()


def get_products(session, category_id: int) -> List[Product]:
    """Возвращает все товары для указанной категории."""
    return session.query(Product).filter_by(category_id=category_id).all()


def send_products_keyboard(products: List[Product]):
    """Возвращает клавиатуру с товарами и кнопку Назад."""
    keyboard = VkKeyboard(one_time=True)
    for p in products:
        keyboard.add_button(p.name, VkKeyboardColor.PRIMARY)
        keyboard.add_line()
    keyboard.add_button("Назад", VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()


def send_message(vk, user_id, text, keyboard=None, attachment=None):
    """Отправляет сообщение пользователю."""
    vk.messages.send(
        user_id=user_id,
        message=text,
        keyboard=keyboard,
        attachment=attachment,
        random_id=random.randint(1, 1_000_000),
    )


def handle_message(vk, user_id: int, text: str):
    """Основная обработка сообщений пользователя."""
    session = SessionLocal()
    user_bot = UserBot(user_id)
    try:

        # START → вывод категорий
        if user_bot.state == "START":
            categories = get_categories(session)
            send_message(
                vk,
                user_id,
                "Приветствуем в магазине выпечки, у нас всегда все самое свежее!\n\nВыберите категорию:",
                keyboard=main_menu_keyboard(categories),
            )
            # меняем state на CATEGORY_SELECTED сразу после показа категорий
            user_bot.state = "CATEGORY_SELECTED"
            user_bot.save_state()
            return

        # CATEGORY_SELECTED → выбранная категория

        elif user_bot.state == "CATEGORY_SELECTED":
            categories = get_categories(session)

            # ---- Назад → на старт (категории)
            if text.lower() == "назад":
                send_message(
                    vk,
                    user_id,
                    "Выберите категорию:",
                    keyboard=main_menu_keyboard(categories),
                )
                user_bot.state = "START"
                user_bot.save_state()
                return

            # ---- Выбор категории ----
            category = _find_by_name(categories, text)
            if category:
                # сохраняем выбранную категорию в контексте
                user_bot.set_context({"category_id": category.id})

                products = get_products(session, category.id)
                if not products:
                    send_message(vk, user_id, "В этой категории пока нет товаров.")
                    return

                send_message(
                    vk,
                    user_id,
                    "Выберите товар:",
                    keyboard=send_products_keyboard(products),
                )
                user_bot.state = "PRODUCT_SELECTED"
                user_bot.save_state()

                return

            send_message(
                vk,
                user_id,
                "Категория не найдена, выберите снова.",
                keyboard=main_menu_keyboard(categories),
            )

            return

        # PRODUCT_SELECTED → выбор товара или кнопка назад

        elif user_bot.state == "PRODUCT_SELECTED":

            ctx = user_bot.get_context()
            category_id = ctx.get("category_id")

            if not category_id:
                categories = get_categories(session)
                send_message(
                    vk,
                    user_id,
                    "Выберите категорию:",
                    keyboard=main_menu_keyboard(categories),
                )
                user_bot.state = "CATEGORY_SELECTED"
                user_bot.save_state()
                return

            # ---- НАЗАД → категории ----
            if text.lower() == "назад":
                categories = get_categories(session)
                send_message(
                    vk,
                    user_id,
                    "Выберите категорию:",
                    keyboard=main_menu_keyboard(categories),
                )
                user_bot.state = "CATEGORY_SELECTED"
                user_bot.save_state()
                return

            # ---- Выбор конкретного товара ----
            products = get_products(session, category_id)
            product = _find_by_name(products, text)
            if product:
                send_message(
                    vk,
                    user_id,
                    f"Название: {product.name}\nОписание: {product.description}\nЦена: {product.price} руб.",
                    attachment=product.vk_attachment,
                )

                keyboard = VkKeyboard(one_time=True)
                keyboard.add_button("Назад", VkKeyboardColor.NEGATIVE)
                send_message(
                    vk, user_id, "Выберите действие:", keyboard=keyboard.get_keyboard()
                )

                user_bot.state = "PRODUCT_DETAILS"
                user_bot.save_state()
                return

            send_message(
                vk,
                user_id,
                "Товар не найден, выберите снова.",
                keyboard=send_products_keyboard(products),
            )
            return

        # PRODUCT_DETAILS → карточка товара
        elif user_bot.state == "PRODUCT_DETAILS":
            ctx = user_bot.get_context()
            category_id = ctx.get("category_id")
            products = get_products(session, category_id)

            if text.lower() == "назад":
                send_message(
                    vk,
                    user_id,
                    "Выберите товар:",
                    keyboard=send_products_keyboard(products),
                )
                user_bot.state = "PRODUCT_SELECTED"
                user_bot.save_state()
                return

            # Любой другой ввод трактуем как попытку выбрать новый товар
            product = _find_by_name(products, text)
            if product:
                send_message(
                    vk,
                    user_id,
                    f"{product.name}\n{product.description}\nЦена: {product.price} руб.",
                    attachment=product.vk_attachment,
                )
                return

            send_message(
                vk,
                user_id,
                "Товар не найден, выберите снова.",
                keyboard=send_products_keyboard(products),
            )

            return
    finally:
        session.close()
        user_bot.close()
