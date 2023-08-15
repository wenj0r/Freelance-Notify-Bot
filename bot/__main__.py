import os, sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from aiogram import Dispatcher, Bot
from aiogram.utils import executor

import re
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from parsers.fl_parser import FL
from parsers.kwork_parser import KWork

from config import USERS, INTERVAL
from loggers import main_logger as logger

from config import TOKEN


def message_from_order(order: dict, tag: str):
    try:
        message = f"<b>{order.get('title').strip()}</b>\n\n" \
            f"<b>Описание:</b> {order.get('description').strip()}\n\n" \
            f"<b>Цена:</b> {order.get('price').strip()}\n"
        if order.get('deadline'):
            message += f"<b>Дедлайн:</b> {order.get('deadline').strip()}\n\n"
        if order.get('category'):
            message += f"<b>Категория:</b> {order.get('category').strip()}\n\n"
        message += f'<a href="{order["link"]}">Ссылка</a>\n\n' \
                   f'#{tag}'

        pattern = r'\xa0'
        message = re.sub(pattern, r'', message)

        return message

    except Exception as e:
        logger.error(f'Не удалось обработать текст заказа.\n{order}')
        logger.exception(e)


async def FL_scheduled():
    new_orders = await fl.update()

    if new_orders:
        for order in new_orders:
            try:
                for user in USERS:
                    text = message_from_order(order, tag='FL')
                    await bot.send_message(user, text, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logger.error(e)


async def KWork_scheduled():
    new_orders = await kw.update()

    if new_orders:
        for order in new_orders:
            try:
                for user in USERS:
                    text = message_from_order(order, tag='KWork')
                    await bot.send_message(user, text, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                logger.error(e)


def start():
    logger.info('Бот вышел в онлайн')
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    time = datetime.now()

    scheduler.add_job(KWork_scheduled, trigger='interval', seconds=INTERVAL, next_run_time=time+timedelta(seconds=5))
    scheduler.add_job(FL_scheduled, trigger='interval', seconds=INTERVAL, next_run_time=time+timedelta(minutes=5))

    scheduler.start()


if __name__ == '__main__':
    fl = FL()
    kw = KWork()
    bot = Bot(token=TOKEN)
    dp = Dispatcher(bot)
    executor.start_polling(dp, skip_updates=True, on_startup=start())

