import os

import vk_api
from vk_api.upload import VkUpload

from src.db.database import SessionLocal, engine
from src.db.models import Base, Category, Product


def init_db(vk_token: str):
    """
    Создает таблицы и наполняет их начальными данными.
    Загружает фотографии товаров в VK и сохраняет attachment.
    """
    # Создаем таблицы
    Base.metadata.create_all(bind=engine)

    # Сессия для работы с БД
    session = SessionLocal()

    # Директория с изображениями
    BASE_DIR = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    IMG_DIR = os.path.join(BASE_DIR, "images")

    # VK загрузчик
    vk_session = vk_api.VkApi(token=vk_token)
    upload = VkUpload(vk_session)

    # Проверяем, пустая ли база
    if session.query(Category).first():
        print("База уже содержит данные. Seed пропущен.")
        session.close()
        return

    # Создаем категории
    categories = [
        Category(name="Хлеб и булки"),
        Category(name="Сладкая выпечка"),
        Category(name="Печенье и пряники"),
        Category(name="Пирожные и торты"),
    ]
    session.add_all(categories)
    session.commit()

    # Список товаров
    products_data = [
        ("Батон", "Хрустящий батон", "Bread-fresh-bread.jpg", 150.0, categories[0].id),
        ("Багет", "Свежий багет", "Bread-baguette.jpg", 120.0, categories[0].id),
        ("Булочка", "Свежая булочка", "Bread-buns.jpg", 80.0, categories[0].id),
        (
            "Круассан",
            "Слоёный круассан с маслом",
            "Sweet-pastries-croissants.jpg",
            50.0,
            categories[1].id,
        ),
        (
            "Классический пирог",
            "Слоёный пирог",
            "Sweet-pastries-pies.jpg",
            90.0,
            categories[1].id,
        ),
        (
            "Печенье",
            "Свежее печенье",
            "Cookies-gingerbread-cookies.jpg",
            95.0,
            categories[2].id,
        ),
        (
            "Пряник",
            "Имбирный пряник",
            "Cookies-gingerbread-gingerbreads.jpg",
            105.0,
            categories[2].id,
        ),
        (
            "Классический наполеон",
            "Классический торт наполеон",
            "Cakes-pies-napoleon.jpg",
            190.0,
            categories[3].id,
        ),
        (
            "Классический медовик",
            "Классический торт медовик",
            "Cakes-pies-medovik.jpg",
            290.0,
            categories[3].id,
        ),
    ]

    # Создаем товары и загружаем фото в VK
    products = []
    for name, desc, filename, price, cat_id in products_data:
        image_path = os.path.join(IMG_DIR, filename)
        if not os.path.exists(image_path):
            print(f"Файл не найден: {image_path}")
            continue

        # Загружаем фото в VK
        try:
            photo = upload.photo_messages(photos=image_path)[0]
            vk_attachment = f"photo{photo['owner_id']}_{photo['id']}"
        except Exception as e:
            print(f"Ошибка загрузки {filename}: {e}")
            vk_attachment = None

        product = Product(
            name=name,
            description=desc,
            image_url=image_path,
            price=price,
            category_id=cat_id,
            vk_attachment=vk_attachment,
        )
        products.append(product)

    session.add_all(products)
    session.commit()
    session.close()
    print("Seed выполнен успешно!")
