import os, sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from pyppeteer import launch
from pyppeteer_stealth import stealth
from fake_useragent import UserAgent
from loggers import main_logger as logger
import pickle
import os
import json
import bs4
import random
import asyncio


ua = UserAgent()
base_url = 'https://kwork.ru/'
cookies_path = './kwork.pickle'


class KWork():
    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self.skip = True
        self.previous_order_links = []
        self.start_parm = {
        'headless' : self.headless,
        'autoClose': False,
        'args' : [
            '--disable-infobars',
            '--ignore-certificate-errors',
            '--log-level = 30',
            f'--user-agent = {ua.random}',
            '--no-sandbox', # с этим параметром нужно вручную выставлять pyppeteer_home
            #f'--proxy-server=http://localhost:1080' # если отделить '=' пробелами - не работает
            '--window-size=1920,1040',
            '--enable-extensions'
            ]
        }


    def parseOrderCard(self, card) -> dict:
        try:
            order = {}
            div = card.find('div', class_='d-flex relative')

            order['title'] = div.find('a').text.strip()
            order['link'] = div.find('a')['href']

            # Получение описания
            hidden = div.find('div', class_='breakwords first-letter overflow-hidden')
            if hidden: order['description'] = hidden.div.text
            else: order['description'] = div.find('div','wants-card__space').text

            # Получение цены
            price_block = div.find('div', class_='wants-card__header-price wants-card__price m-hidden')
            order['price'] = price_block.find('span', {'lang': 'ru'}).text.strip()
            if 'до' in price_block.find('span', class_='fs12').text:
                order['price'] = 'до ' + order['price']

            return order
        except Exception as e:
            logger.error(f'[KWORK] Не получилось спарсить объявление')
            logger.exception(e)


    def parseNewOrders(self, content) -> list:
        new_orders = []
        soup = bs4.BeautifulSoup(content, 'lxml')
        cards = soup.find_all('div', class_='card__content pb5')
        for card in cards:
            order = self.parseOrderCard(card)

            if order and not order['link'] in self.previous_order_links:
                self.previous_order_links.append(order['link'])
                # Финальная ссылка добавляется только в новые объявления
                order['link'] = base_url + order['link'][1:]
                new_orders.append(order)

        # Список передыдущих заказов содержит только последние 2000 заказа
        lenght = len(self.previous_order_links)
        if lenght > 2000:
            self.previous_order_links = self.previous_order_links[lenght-2000:]

        if not self.skip:
            return new_orders


    async def firstLaunch(self) -> None:
        if self.start_parm['headless']:
            self.start_parm['headless'] = False

            self.browser = await launch(options=self.start_parm)
            self.main_page = await self.browser.newPage()
            await self.main_page.setViewport(viewport={'width': 1920, 'height': 1040})
            await self.main_page.goto('https://kwork.ru/')

            await self.main_page.waitForResponse('https://kwork.ru/projects?a=1', timeout=0)
            cookies = await self.main_page.cookies()
            with open(cookies_path, 'wb') as f:
                pickle.dump(cookies, f)

            await self.browser.close()
            self.start_parm['headless'] = self.headless


    async def update(self) -> list:
        if not os.path.exists(cookies_path):
            await self.firstLaunch()

        browser = await launch(options=self.start_parm)
        page = await browser.newPage()
        await page.setViewport(viewport={'width': 1920, 'height': 1040})
        await stealth(page)

        with open(cookies_path, 'rb') as f:
            cookies = pickle.load(f)
            await page.setCookie(*cookies)
            await page.reload()

        # Выдаст результат только, если история не пуста
        if self.previous_order_links: 
            self.skip = False

        orders = []
        num = 1
        while True:
            url = base_url+f'projects?a=1&page={num}'
            resp = await page.goto(url)

            if not url == resp.url:
                break

            logger.debug(f'[KWORK] Обработка страницы #{num}')
            content = await page.content()
            
            
            new_orders = self.parseNewOrders(content=content)
            if new_orders: orders += new_orders
            
            await asyncio.sleep(1)
            num += 1

        logger.debug(f'\n[KWORK] Новых запросов: {len(orders)}')
        await browser.close()

        return orders

kw = KWork()

loop = asyncio.get_event_loop()
loop.run_until_complete(kw.update())     


