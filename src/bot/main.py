import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from src.bot.handlers import handle_message
from src.db.seed import init_db


load_dotenv()
BOT_TOKEN = os.getenv("VK_GROUP_TOKEN")
init_db(BOT_TOKEN)


vk_session = vk_api.VkApi(token=BOT_TOKEN)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

print("Бот запущен...")

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        user_id = event.user_id
        text = event.text
        handle_message(vk, user_id, text)
