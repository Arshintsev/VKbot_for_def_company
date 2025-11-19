import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()  # загружаем .env

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///vk_bot.db")
SQL_ECHO = os.getenv("SQL_ECHO", "False").lower() == "true"

engine = create_engine(DATABASE_URL, echo=SQL_ECHO, future=True)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
