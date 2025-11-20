from transitions import Machine

from src.db.database import SessionLocal
from src.db.models import UserSession


class UserBot:
    """
    Класс для работы с состояниями пользователя через машину состояний.
    Сохраняет состояние и context в базе данных.
    """
    state: str
    states = ["START", "CATEGORY_SELECTED", "PRODUCT_SELECTED", "PRODUCT_DETAILS"]

    def __init__(self, user_id):
        self.session_db = SessionLocal()
        # получаем или создаём сессию пользователя
        user = self.session_db.query(UserSession).filter_by(user_id=user_id).first()
        if not user:
            user = UserSession(user_id=user_id, state="START")
            self.session_db.add(user)
            self.session_db.commit()
            self.session_db.refresh(user)
        self.user = user

        # создаём машину состояний
        self.machine = Machine(
            model=self, states=UserBot.states, initial=self.user.state, send_event=True
        )

        # определяем переходы
        self.machine.add_transition(
            trigger="choose_category",
            source="START",
            dest="CATEGORY_SELECTED",
        )
        self.machine.add_transition(
            trigger="choose_product",
            source="CATEGORY_SELECTED",
            dest="PRODUCT_SELECTED",
        )
        self.machine.add_transition(
            trigger="go_back",
            source="CATEGORY_SELECTED",
            dest="START",
        )
        self.machine.add_transition(
            trigger="view_product",
            source="PRODUCT_SELECTED",
            dest="PRODUCT_DETAILS",
        )
        self.machine.add_transition(
            trigger="back_to_products",
            source="PRODUCT_DETAILS",
            dest="PRODUCT_SELECTED",
        )
        self.machine.add_transition(
            trigger="go_back_from_product",
            source="PRODUCT_SELECTED",
            dest="CATEGORY_SELECTED",
        )
        self.machine.add_transition(
            trigger="go_back_from_details",
            source="PRODUCT_DETAILS",
            dest="CATEGORY_SELECTED",
        )

    def save_state(self):
        """Сохраняем текущее состояние в базе."""
        self.user.state = self.state
        self.session_db.commit()

    def get_context(self) -> dict:
        """Возвращает context через UserSession."""
        return self.user.get_context()

    def set_context(self, data: dict):
        """Сохраняет context через UserSession."""
        self.user.set_context(data)
        self.session_db.commit()

    def close(self):
        """Закрывает сессию БД."""
        self.session_db.close()
