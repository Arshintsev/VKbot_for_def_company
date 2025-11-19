from database import SessionLocal, engine
from models import Base, Category, Product

# Создаем все таблицы
Base.metadata.create_all(bind=engine)

# Сессия для работы с БД
session = SessionLocal()

# Проверяем, пустая ли база
if session.query(Category).first():
    print("База уже содержит данные. Seed пропущен.")
else:
    # Создаем категории
    categories = [
        Category(name="Хлеб и булки"),
        Category(name="Сладкая выпечка"),
        Category(name="Печенье и пряники"),
        Category(name="Пирожные и торты"),
    ]
    session.add_all(categories)
    session.commit()

    # Создаем товары
    products = [
        Product(
            name="Батон",
            description="Хрустящий батон",
            image_url="images/Bread-bread.jpg",
            price=150.00,
            category_id=categories[0].id,
        ),
        Product(
            name="Багет",
            description="Свежий багет",
            image_url="images/Bread-baguette.jpg",
            price=120.00,
            category_id=categories[0].id,
        ),
        Product(
            name="Булочка",
            description="Свежая булочка",
            image_url="images/Bread-buns.jpg",
            price=800.00,
            category_id=categories[0].id,
        ),
        Product(
            name="Круассан",
            description="Слоёный круассан с маслом",
            image_url="images/Sweet-pastries-croissants.jpg",
            price=50.00,
            category_id=categories[1].id,
        ),
        Product(
            name="Классический пирог",
            description="Слоёный круассан с маслом",
            image_url="images/Sweet-pastries-pies.jpg",
            price=90.00,
            category_id=categories[1].id,
        ),
        Product(
            name="Печенье",
            description="Свежее печенье",
            image_url="images/Cookies-gingerbread-cookies.jpg",
            price=95.00,
            category_id=categories[2].id,
        ),
        Product(
            name="Пряник",
            description="Имбирный пряник",
            image_url="images/Cookies-gingerbread-gingerbreads.jpg",
            price=105.00,
            category_id=categories[2].id,
        ),
        Product(
            name="Классический наполен",
            description="Классический торт наполеон",
            image_url="images/Cakes-pies-napoleon.jpg",
            price=190.00,
            category_id=categories[3].id,
        ),
        Product(
            name="Классический медовик",
            description="Классический торт медовик",
            image_url="images/Cakes-pies-medovik.jpg",
            price=290.00,
            category_id=categories[3].id,
        ),
    ]
    session.add_all(products)
    session.commit()
    print("Seed выполнен успешно!")

session.close()
