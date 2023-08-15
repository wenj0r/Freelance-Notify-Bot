from pyppeteer import launch
from pyppeteer_stealth import stealth
import bs4
import re
from fake_useragent import UserAgent

from loggers import main_logger as logger
import pickle
import os


ua = UserAgent()
base_url = 'https://www.fl.ru/projects/'
cookies_path = './fl.pickle'

class FL():
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.previous_orders_id = []
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


    async def parseOrders(self, content):
        soup = bs4.BeautifulSoup(content, 'lxml')
        divs = soup.find_all('div', id=re.compile('project-item'))

        orders = []
        for div in divs:
            id = div.h2.a['href'].split('/')[2]
            orders.append(id)
        return orders


    async def getOrderInfo(self, id: str):
        logger.debug(f'Обрабатывается объявление #{id}')
        url = base_url + id
        
        page = await self.browser.newPage()
        await page.setViewport(viewport={'width': 1920, 'height': 1040})
        await stealth(page)

        await page.goto(url, {'waitUntil': 'networkidle2'})
        await page.waitForXPath("(//div[contains(@class, 'b-layout')])")

        content = await page.content()
        order = self.parseOrderPage(content)

        await page.close()
        
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

        return new_orders_id


    async def update(self):
        # ФУНКЦИЯ ДЛИННАЯ, Я УЖЕ ПОДЪУСТАЛ
        # КОЛХОЗ, ДА. ЗДЕСЬ ПОЛЬЗОВАТЕЛЬ ЗАПОЛНЯЕТ ФИЛЬТРЫ, ЕСЛИ ПЕЧЕНЕК НЕТ
        if not os.path.exists(cookies_path):
            if self.start_parm['headless']:
                self.start_parm['headless'] = False

                self.browser = await launch(options=self.start_parm)
                self.main_page = await self.browser.newPage()
                await self.main_page.setViewport(viewport={'width': 1920, 'height': 1040})
                await self.main_page.goto('https://fl.ru/projects')

                await self.main_page.waitForResponse('https://www.fl.ru/projects/session/filter/', timeout=0)
                cookies = await self.main_page.cookies()
                with open(cookies_path, 'wb') as f:
                    pickle.dump(cookies, f)

                await self.browser.close()
                self.start_parm['headless'] = self.headless

        # Полноценный запуск браузера
        self.browser = await launch(options=self.start_parm)

        self.main_page = await self.browser.newPage()
        await self.main_page.setViewport(viewport={'width': 1920, 'height': 1040})
        await stealth(self.main_page)

        await self.main_page.goto('https://fl.ru/projects')

        with open(cookies_path, 'rb') as f:
            cookies = pickle.load(f)
            await self.main_page.setCookie(*cookies)
            await self.main_page.reload()

        # Парсинг новых заказов
        content = await self.main_page.content()
        order_ids = await self.parseOrders(content)
        new_orders_ids = self.newOrdersCheck(order_ids)
        logger.debug(f'\n[FL] Проверка... Новых запросов: {new_orders_ids}')

        new_orders = []
        for order_id in new_orders_ids:
            order = await self.getOrderInfo(order_id)
            if order:
                new_orders.append(order)

        logger.debug(f'[FL] Всего обработано запросов: {len(self.previous_orders_id)}')
        await self.browser.close()

        return new_orders