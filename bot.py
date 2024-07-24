# To Fix "cannot switch to a different thread" Error
from gevent import monkey
monkey.patch_all()

from aiogram import Bot
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import re
import asyncio

from fl_parser import FL
from kwork_parser import KWork
from config import TOKEN, USERS, INTERVAL
from loggers import main_logger as logger


def makeMessage(order: dict, tag: str):
    try:
        message = f"<b>{order.get('title').strip()}</b>\n\n" \
            f"<b>Описание:</b> {order.get('description').strip()}\n\n" \
            f"<b>Цена:</b> {order.get('price').strip()}\n"
        if order.get('deadline'):
            message += f"<b>Дедлайн:</b> {order.get('deadline').strip()}\n\n"
        if order.get('category'):
            message += f"<b>Категория:</b> {order.get('category').strip()}\n"
        message += f'\n<a href="{order["link"]}">Ссылка</a>\n\n' \
                   f'#{tag}'

        pattern = r'\xa0'
        message = re.sub(pattern, r'', message)

        return message

    except Exception as e:
        logger.error(f'Не удалось обработать текст заказа.\n{order}')
        logger.exception(e)

async def sendMessage(msg: str):
    async with Bot(token=TOKEN) as bot:
        for user in USERS:
            try:
                await bot.send_message(user, msg, parse_mode='HTML', disable_web_page_preview=True)
            except Exception as e:
                    logger.error(e)

def FLScheduled():
    new_orders = fl.getNewOrders()
    if new_orders:
        for order in new_orders:
            text = makeMessage(order, tag='FL')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(sendMessage(text))


def KWorkScheduled():
    new_orders = kw.getNewOrders()
    if new_orders:
        for order in new_orders:
            text = makeMessage(order, tag='KWORK')
            loop = asyncio.get_event_loop()
            loop.run_until_complete(sendMessage(text))


if __name__ == '__main__':
    fl = FL()
    kw = KWork()
    bot = Bot(token=TOKEN)
    
    scheduler = BlockingScheduler(timezone="Europe/Moscow")
    scheduler.add_job(KWorkScheduled, trigger='interval', seconds=INTERVAL, next_run_time=datetime.now()+timedelta(seconds=5))
    scheduler.add_job(FLScheduled, trigger='interval', seconds=INTERVAL, next_run_time=datetime.now()+timedelta(seconds=30))
    scheduler.start()
