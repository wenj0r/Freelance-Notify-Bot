# To Fix "cannot switch to a different thread" error on Raspberry Pi
from gevent import monkey
monkey.patch_all()

import requests
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import re

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

def sendMessage(msg: str):
    for user in USERS:
        json_data = {'chat_id': user,
                    'text': msg,
                    'parse_mode': 'HTML',
                    'link_preview_options': {'is_disabled': True}}
    
        attempts = 1
        while attempts <= 3: 
            try:
                resp = requests.post('https://api.telegram.org/bot'+TOKEN+'/sendMessage', json=json_data)
                if resp.status_code == 200:
                    break
                else:
                    logger.error('Не получилось отправить сообщение в Telegram')
            except Exception as e:
                logger.error(e)
                
            attempts += 1

def FLScheduled():
    new_orders = fl.getNewOrders()
    if new_orders:
        for order in new_orders:
            text = makeMessage(order, tag='FL')
            sendMessage(text)


def KWorkScheduled():
    new_orders = kw.getNewOrders()
    if new_orders:
        for order in new_orders:
            text = makeMessage(order, tag='KWORK')
            sendMessage(text)


if __name__ == '__main__':
    fl = FL()
    kw = KWork()
    
    scheduler = BlockingScheduler(timezone="Europe/Moscow")
    scheduler.add_job(KWorkScheduled, trigger='interval', seconds=INTERVAL, next_run_time=datetime.now()+timedelta(seconds=5))
    scheduler.add_job(FLScheduled, trigger='interval', seconds=INTERVAL, next_run_time=datetime.now()+timedelta(seconds=30))
    scheduler.start()