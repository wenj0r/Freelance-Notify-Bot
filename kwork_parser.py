from loggers import main_logger as logger
from random import randint
import requests
import time

from config import KWORK_MAIL, KWORK_PASS, KWORK_COOKIES

base_url = 'https://kwork.ru/'
cookies_path = './cookies/kwork.pickle'


class KWork():
    def __init__(self) -> None:
        self.skip = True
        self.previous_orders_id = []
        self.expire = 0
        self.cookies = KWORK_COOKIES
        
        self.headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }


    def updateCookies(self):
        data = {
            "l_username": KWORK_MAIL,
            "l_password": KWORK_PASS,
            "jlog": 1,
            "recaptcha_pass_token": "",
            "g-recaptcha-response": "",
            "track_client_id": False,
            "l_remember_me": "1"
            }
        
        resp = requests.post(base_url+'api/user/login', json=data, headers=self.headers, cookies=self.cookies)
        if resp.status_code == 200:
            self.expire = next(cookie.expires for cookie in resp.cookies)
            self.cookies = resp.cookies.get_dict()
        else:
            logger.error('Не получилось авторизоваться в KWork')
    
    
    def parseNewOrders(self, ads) -> dict:
        new_orders = []
        for ad in ads:
            order = {
                'title': ad.get('name'),
                'id': str(ad.get('id')),
                'description': ad.get('description'),
                'price': 'до '+ ad.get('priceLimit').split(',')[0]
            }
            if not order['id'] in self.previous_orders_id:
                self.previous_orders_id.append(order['id'])
                
                if not self.skip:
                    order['link'] = base_url + order['id']
                    new_orders.append(order)
                
                # Список передыдущих заказов содержит только последние 2000 заказа
                lenght = len(self.previous_orders_id)
                if lenght > 2000:
                    self.previous_orders_id = self.previous_orders_id[lenght-2000:]
        
        return new_orders
            


    def getNewOrders(self) -> list:      
        if time.time() >= self.expire:
            self.updateCookies()

        # Выдаст результат только, если история не пуста
        if self.previous_orders_id: 
            self.skip = False
        else:
            logger.info('[KWORK] Первый запуск. Собираем существующие заказы...')

        orders = []
        page = 1
        max_pages = 1
        while page <= max_pages:
            json_data = {
                'a': 1,
                'page': page
            }
            
            resp = requests.post(base_url+f'projects', json=json_data, headers=self.headers, cookies=self.cookies)
            if resp.status_code == 200:
                logger.debug(f'[KWORK] Обработка страницы #{page}')
                data = resp.json()
                max_pages = data['data']["pagination"]['last_page']
                ads = data['data']['pagination']['data']
                new_orders = self.parseNewOrders(ads)
                if new_orders: orders += new_orders
            else:
                logger.error(f'[KWORK] Не получилось обработать #{page}')
            
            time.sleep(randint(1,2))
            page += 1

        logger.debug(f'[KWORK] Новых запросов: {len(orders)}')
        logger.debug(f'[KWORK] Всего обработано запросов: {len(self.previous_orders_id)}')

        return orders

