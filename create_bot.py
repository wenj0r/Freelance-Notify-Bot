from aiogram import types, Dispatcher, Bot
from dotenv import load_dotenv
from os import getenv
import re

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsers.fl_parser.parser import FL

from config import users, update_interval
from loggers import main_logger as logger
load_dotenv()

TOKEN = getenv('TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


"""
Поведение бота нужно описывать с помощью обработчиков. Ниже обычный echo для примера.
Специфическую логику работы бота, например рассылку, можно сделать в отдельном файле bot.py и просто подгрузить в main.py
"""

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer('ЮХУУУУ')

# fl = FL()

def message_from_order(order: dict):
    url = 'https://www.fl.ru/projects/' + order['id']

    message = f"<b>{order['title'].strip()}</b>\n\n" \
        f"<b>Категория:</b> {order['category'].strip()}\n\n" \
        f"<b>Описание:</b> {order['description'].strip()}\n\n" \
        f"<b>Цена:</b> {order['price'].strip()}\n" \
        f"<b>Дедлайн:</b> {order['deadline'].strip()}\n\n" \
        f'<a href="{url}">Ссылка</a>'

    pattern = r'\xa0'
    message = re.sub(pattern, r'', message)

    return message

fl = FL()
async def scheduled():
    new_orders = await fl.update_all()
    if new_orders:
        for order in new_orders:
            for user in users:
                await bot.send_message(user, message_from_order(order), parse_mode='HTML', disable_web_page_preview=True)


async def start():
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(scheduled, trigger='interval', seconds=update_interval)
    scheduler.start()


# if __name__ == '__main__':
#     order = {'category': 'Дизайн и Арт / Дизайн интерфейсов приложений',
#             'date': 'Fri, 28 Jul 2023 10:52:22 GMT',
#             'deadline': '31.08.2023',
#             'description': """
#             Нужно сделать дизайн мобильного приложения для
#             интернет магазина.\xa0 Есть новый макет мобильной версии
#             сайта, опираться\xa0 нужно на него в концептуальном плане.
#             Есть фирменная айдентика. От дизайнера требуется глубокое
#             погружение в бизнес процессы, чтобы сделать удобный дизайн на
#             пользователей.\xa0 Макет, дательное ТЗ после выбора
#             фрилансера в качестве кандидата. ОБЯЗЕЛЕН ОПЫТ В ДИЗАЙНЕ
#             МОБ.ПРИЛОЖЕНИЙ. ОБЕЗАТЕЛЬНО ПРИКРЕЛЯЙТЕ КЕЙСЫ С МОБ.
#             ПРИЛОЖЕНИЯМИ К ОТКЛИКУ!!
#         """,
#         'for_all': False,
#         'id': '5201709',
#         'price': '100 000 руб/заказ',
#         'title': 'Дизайн мобильного приложения  \(Бюджет: 100000  &#8381;\)'}
#     print(message_from_order(order))