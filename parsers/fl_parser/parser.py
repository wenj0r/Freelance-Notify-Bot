from aiohttp import ClientSession
import os, sys 
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import asyncio
from time import sleep

import bs4
import re

from fake_useragent import FakeUserAgent

from rss import get_rss, parse_rss
from pprint import pprint

ua = FakeUserAgent()
sub_categories_id = []

from pyppeteer import launch
from pyppeteer_stealth import stealth


def parse_order_page(content):
    # with open('output.html', 'r', encoding='utf-8') as f:
    #     content = f.read()

    extra = {'for_all': False,
            'price': 0,
            'deadline': '',
            'description': ''
            }

    soup = bs4.BeautifulSoup(content, 'lxml')
    
    # Проверка для всех ли пользователей
    if soup.find('span', {'data-tip-txt': 'Отвечать могут все фрилансеры'}):
        extra['for_all'] = True

    # Получение описания
    extra['description'] = soup.find(attrs={"id": re.compile('projectp')}).text

    # Получение цены и дедлайна
    div = soup.find('div', class_=re.compile('unmobile flex-shrink'))
    
    divs = div.find_all('div', class_=re.compile('text-4'))
    extra['price'] = divs[0].span.text.strip()
    extra['deadline'] = divs[1].span.text.strip()

    return extra


async def get_more_info(order: dict):

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

    url = order.get('link')
    browser = await launch(start_parm)
    page = await browser.newPage()
    await page.setViewport(viewport={'width': 1920, 'height': 1040})
    await stealth(page)

    await page.goto(url, {'waitUntil': 'networkidle2'})
    await page.waitForXPath("(//div[contains(@class, 'b-layout')])")

    content = await page.content()

    extra = parse_order_page(content)
    order.update(extra)
    print(order)

    # with open('output.html', 'w', encoding='utf-8') as f:
    #     f.write(content)

 
async def check_new_orders(orders: list):
    pass


async def filter(order: dict):
    pass


async def response_order(url: str, text: str):
    pass


if __name__ == '__main__':
    # with open('all.xml', encoding="utf8") as file:
    #     xml = file.read()

    loop = asyncio.get_event_loop()
    #loop.run_until_complete(make_screenshot('https://www.fl.ru/projects/5200050/2d-igra-dlya-obucheniya-.html'))
    order = {'link': 'https://www.fl.ru/projects/5199218/skachivanie-podborok-springer-elsevier-.html'}
    loop.run_until_complete(get_more_info(order))