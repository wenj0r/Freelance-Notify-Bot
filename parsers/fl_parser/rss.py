from aiohttp import ClientSession
import bs4
from parsers import network

async def get_rss(main_cat: int= None, sub_cat: int = None):
    rss_url = f'https://www.fl.ru/rss/all.xml'
    params = {
            'category': main_cat,
            'subcategory': sub_cat
            }

    async with ClientSession() as s:
        resp = await network._get(s, rss_url)
        
        if resp:
            content = await resp.read()
            return content.decode()


async def parse_rss(xml):
    orders = []
    soup = bs4.BeautifulSoup(xml, 'xml')
    items = soup.find_all('item')
    for item in items:
        order = {
                'title':  item.find('title').text,
                'description': item.find('description').text,
                'category': item.find('category').text,
                'link': item.find('link').text,
                'date': item.find('pubDate').text
                }
    return orders