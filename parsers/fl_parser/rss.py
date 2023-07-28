import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import asyncio

from aiohttp import ClientSession
import bs4
from parsers import network

async def get_rss(main_cat: int= None, sub_cat: int = None):
    rss_url = f'https://www.fl.ru/rss/all.xml'
    
    params = {}
    if main_cat: params['category'] = main_cat
    if sub_cat: params['subcategory'] = sub_cat

    async with ClientSession() as s:
        resp = await network._get(s, rss_url, params=params)
        if resp:
            content = await resp.read()
            return content.decode()


def parse_rss(xml):
    orders = []
    soup = bs4.BeautifulSoup(xml, 'xml')
    items = soup.find_all('item')
    for item in items:
        order = {
                'title':  item.find('title').text,
                'description': item.find('description').text,
                'category': item.find('category').text,
                'id': item.find('link').text.split('/')[4],
                'date': item.find('pubDate').text
                }
        orders.append(order)
    return orders


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    content = loop.run_until_complete(get_rss(1))
    orders = parse_rss(content)