from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
import bs4
import re

from loggers import main_logger as logger
import pickle
import os

base_url = 'https://www.fl.ru/projects/'
cookies_path = './cookies/fl.pickle'

class FL():
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.previous_orders_id = []
        self.skip = True
        
        self.pw = sync_playwright().start()


    def parseOrders(self, content):
        soup = bs4.BeautifulSoup(content, 'lxml')
        divs = soup.find_all('div', id=re.compile('project-item'))

        orders = []
        for div in divs:
            id = div.h2.a['href'].split('/')[2]
            orders.append(id)
        return orders


    def getOrderInfo(self, id: str):
        logger.debug(f'Обрабатывается объявление #{id}')
        url = base_url + id
        
        page = self.browser.new_page()
        stealth_sync(page)

        page.goto(url)
        page.wait_for_load_state()

        content = page.content()
        order = self.parseOrderPage(content)

        page.close()
        
        if order:
            order['id'] = id
            order['link'] = 'https://www.fl.ru/projects/' + id
            return order
        else:
            logger.debug(f"[FL] Заказ #{id} пропущен")
            return         


    def parseOrderPage(self, content):
        order = {}
        soup = bs4.BeautifulSoup(content, 'lxml')
        try: 

            # Проверка на исполнителя
            if soup.find('span', text=re.compile('Исполнитель определен')): 
                return

            # Проверка для всех ли пользователей
            if soup.find('span', attrs={'data-tip-width': 140}):
                order['for_all'] = True

            # Получение описания
            order['title'] = soup.find('h1', class_=re.compile('text-1')).text
            order['description'] = soup.find(attrs={"id": re.compile('projectp')}).text

            # Получение категории
            div = soup.find('div', class_=re.compile('b-layout_overflow_hidden')).find('div', class_=re.compile('text-5 mb-4'))
            a = div.find_all('a')
            category = a[0].text
            subcategory = a[1].text
            order['category'] = f'{category} - {subcategory}'

            # Получение цены и дедлайна
            div = soup.find('div', class_=re.compile('unmobile flex-shrink'))
            divs = div.find_all('div', class_=re.compile('text-4'))
            if divs[0]: order['price'] = divs[0].span.text.strip()
            if divs[1]: order['deadline'] = divs[1].span.text.strip()

            return order

        except Exception as e:
            logger.exception(e)
            return


    def newOrdersCheck(self, orders_id: list):
        new_orders_id = []
        for order_id in orders_id:
            if not order_id in self.previous_orders_id:
                new_orders_id.append(order_id)

        self.previous_orders_id += new_orders_id

        # Список передыдущих заказов содержит только последние 2000 заказа
        lenght = len(self.previous_orders_id)
        if lenght > 2000:
            self.previous_orders_id = self.previous_orders_id[lenght-2000:]

        if not self.skip:
            return new_orders_id
        else:
            return []


    def getCookies(self):
        self.browser = self.pw.chromium.launch(headless=False)
        page = self.browser.new_page()
        stealth_sync(page)
        page.goto('https://fl.ru')
        page.wait_for_load_state()
        page.wait_for_selector("xpath=//a[contains(.,'Мои отклики')]", timeout=0)
        
        cookies = page.context.cookies()
        self.browser.close()

        if not os.path.exists('./cookies'):
            os.mkdir('./cookies')
        with open(cookies_path, 'wb') as f:
            pickle.dump(cookies, f)


    def getNewOrders(self):
        if not os.path.exists(cookies_path):
            self.getCookies()

        # Полноценный запуск браузера
        self.browser = self.pw.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context()

        with open(cookies_path, 'rb') as f:
            cookies = pickle.load(f)
            self.context.add_cookies(cookies)

        self.main_page = self.context.new_page()
        stealth_sync(self.main_page)
        self.main_page.goto('https://fl.ru/projects')
        
        # Выдаст результат только, если история не пуста 
        if self.previous_orders_id:
            self.skip = False
        else:
            logger.info('[FL] Первый запуск. Собираем существующие заказы...')

        # Парсинг новых заказов
        content = self.main_page.content()
        order_ids = self.parseOrders(content)
        new_orders_ids = self.newOrdersCheck(order_ids)
        logger.debug(f'[FL] Новых запросов: {len(new_orders_ids)}')

        new_orders = []
        if new_orders_ids:
            for order_id in new_orders_ids:
                order = self.getOrderInfo(order_id)
                if order:
                    new_orders.append(order)

        logger.debug(f'[FL] Всего обработано запросов: {len(self.previous_orders_id)}')
        self.browser.close()

        return new_orders