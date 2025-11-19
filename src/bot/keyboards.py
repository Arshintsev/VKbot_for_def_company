from vk_api.keyboard import VkKeyboard, VkKeyboardColor


def main_menu_keyboard(categories):
    """Создает вертикальную клавиатуру с категориями."""
    keyboard = VkKeyboard(one_time=True)
    for i, cat in enumerate(categories):
        keyboard.add_button(cat.name, color=VkKeyboardColor.PRIMARY)
        if (
            i != len(categories) - 1
        ):  # добавляем новую строку только если это не последняя кнопка
            keyboard.add_line()
    return keyboard.get_keyboard()


def back_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()
