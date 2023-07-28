import os, sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import asyncio
from pyppeteer import launch
from pyppeteer_stealth import stealth
import bs4
import re
from fake_useragent import UserAgent
from .rss import get_rss, parse_rss
from random import randint
from config import subcategories

import time


ua = UserAgent()
base_url = 'https://www.fl.ru/projects/'


class FL():
    def __init__(self):
        self.last_ids = {}

    def parse_order_page(self, content):
        # with open('output.html', 'r', encoding='utf-8') as f:
        #     content = f.read()

        extra = {'for_all': False,
                'price': 0,
                'deadline': '',
                'description': ''
                }
        soup = bs4.BeautifulSoup(content, 'lxml')

        try: 
            # Проверка для всех ли пользователей
            if soup.find('span', attrs={'data-tip-width': 140}):
                extra['for_all'] = True

            # Получение описания
            extra['description'] = soup.find(attrs={"id": re.compile('projectp')}).text

            # Получение цены и дедлайна
            div = soup.find('div', class_=re.compile('unmobile flex-shrink'))
            
            divs = div.find_all('div', class_=re.compile('text-4'))
            extra['price'] = divs[0].span.text.strip()
            extra['deadline'] = divs[1].span.text.strip()
        except Exception as e:
            print(e)
            return None

        return extra


    async def get_more_info(self, order: dict):

        start_parm = {
        'headless' : False,
        'args' : [
            '--disable-infobars',
            '--ignore-certificate-errors',
            '--log-level = 30',
            f'--user-agent = {ua.random}',
            '--no-sandbox', # с этим параметром нужно вручную выставлять pyppeteer_home
            #f'--proxy-server=http://localhost:1080' # если отделить '=' пробелами – не работает
            '--window-size=1920,1040',
            '--enable-extensions',
            ],
        }

        url = base_url+order.get('id')
        browser = await launch(start_parm)
        page = await browser.newPage()
        await page.setViewport(viewport={'width': 1920, 'height': 1040})
        await stealth(page)

        await page.goto(url, {'waitUntil': 'networkidle2'})
        await page.waitForXPath("(//div[contains(@class, 'b-layout')])")

        content = await page.content()

        extra = self.parse_order_page(content)
        order.update(extra)

        return order

        # with open('output.html', 'w', encoding='utf-8') as f:
        #     f.write(content)


    def get_new_orders_in_category(self, orders: list, subcategory: int = None):
        # На случай, если скрипт только запустили
        if not self.last_ids.get(subcategory):
            self.last_ids[subcategory] = orders[0].get('id')
            return

        # Поочередно сравнивает последний известный id с заказами, и если находит – то обрезает список
        last_id = self.last_ids.get(subcategory)
        for i, order in enumerate(orders):
            if order.get('id') == last_id:
                self.last_ids[subcategory] = orders[0].get('id')
                orders = orders[:i]
                break

        return orders


    async def filter(self, order: dict):
        pass


    async def response_order(self, url: str, text: str):
        pass


    async def check_category_for_update(self, subcategory: int = None):
        content = await get_rss(sub_cat=subcategory)
        orders = parse_rss(content)
        
        if orders:
            new_orders = self.get_new_orders_in_category(orders, subcategory)

            if new_orders:
                for order in new_orders:
                    order = self.get_more_info(order)
                    if not order:
                        orders.remove(order)
                    await asyncio.sleep(randint(1,5))
            return new_orders


    async def update_all(self):
        new_orders = []
        for subcategory in subcategories:
            cat_new_orders = await self.check_category_for_update(subcategory)
            if cat_new_orders:
                new_orders += cat_new_orders
            
        return new_orders


if __name__ == '__main__':

    # with open('all.xml', encoding="utf8") as file:
    #     xml = file.read()
    # import pprint
    # parser = FL()
    # loop = asyncio.get_event_loop()
    # content = loop.run_until_complete(get_rss())
    # orders = parse_rss(content)
    # order = loop.run_until_complete(parser.get_more_info(orders[1]))
    # pprint.pprint(order)

    # loop.run_until_complete(make_screenshot('https://www.fl.ru/projects/5200050/2d-igra-dlya-obucheniya-.html'))
    # order = {'link': 'https://www.fl.ru/projects/5201518/razrabotat-avtomatizirovannyiy-raschet-kp-na-osnove-praysa-po-oborudovaniyu-i-praysa-po-rabotam.html'}
    # loop.run_until_complete(get_more_info(order))
    list = [1,2,3,4,5]
    for i, item in enumerate(list):
        if item == 4:
            list.remove(i)
        print(item)