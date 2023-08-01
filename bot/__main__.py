import os, sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

print(sys.path)
from aiogram import types, Dispatcher, Bot
from aiogram.utils import executor

import re

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsers.fl_parser import FL

from config import USERS, INTERVAL
from loggers import main_logger as logger

from config import TOKEN


def message_from_order(order: dict):
    url = 'https://www.fl.ru/projects/' + order['id']

    try:
        message = f"<b>{order.get('title').strip()}</b>\n\n" \
            f"<b>Описание:</b> {order.get('description').strip()}\n\n" \
            f"<b>Цена:</b> {order.get('price').strip()}\n" \
            f"<b>Дедлайн:</b> {order.get('deadline').strip()}\n\n" \
            f"<b>Категория:</b> {order.get('category').strip()}\n\n" \
            f'<a href="{url}">Ссылка</a>'

        pattern = r'\xa0'
        message = re.sub(pattern, r'', message)

        return message

    except Exception as e:
        logger.error(f'Не удалось обработать текст заказа.\n{order}')
        logger.exception(e)


async def scheduled():
    new_orders = await fl.update()

    if new_orders:
        for order in new_orders:
            for user in USERS:
                await bot.send_message(user, message_from_order(order), parse_mode='HTML', disable_web_page_preview=True)


def start():
    logger.info('Бот вышел в онлайн')
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(scheduled, trigger='interval', seconds=INTERVAL)
    scheduler.start()


if __name__ == '__main__':
    fl = FL()
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)
    executor.start_polling(dp, skip_updates=True, on_startup=start())

