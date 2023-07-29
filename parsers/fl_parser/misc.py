import requests
import json
import bs4

import json
with open('subcategories.json', encoding='UTF-8') as f:
    subcategories_list = json.load(f) 


def get_category_ids():
    rss_url = f'https://www.fl.ru/rss/all.xml'
    categories = {}
    sub_categories = {}

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36 AVG/74.0.791.133',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.fl.ru/projects/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Sec-GPC': '1',
    }

    for i in range(1, 100):
        params = {'category': i}
        content = requests.get(rss_url, params=params, headers=headers).content.decode()
        soup = bs4.BeautifulSoup(content, 'xml')

        name = soup.find('title')
        # Обработка результата
        try:
            name = name.text
            res = name.split('Все заказы: ')
            if res:
                name = res[1][:-1]
            else:
                i -= 1
                continue
            categories[i] = name
        except IndexError:
            continue
        except Exception as e:
            print(e)        


    for i in range(1, 1000):
        params = {'subcategory': i}
        content = requests.get(rss_url, params=params, headers=headers).content.decode()
        soup = bs4.BeautifulSoup(content, 'xml')

        name = soup.find('title')
        # Обработка результата
        try:
            name = name.text
            res = name.split('Все заказы: ')
            if res:
                name = res[1][:-1]
            else:
                i -= 1
                continue
            sub_categories[i] = name
        except IndexError:
            continue
        except Exception as e:
            print(e) 


    with open('categories.json', 'w', encoding='utf-8') as file:
        json.dump(categories, file, indent=4, ensure_ascii=False)

    with open('subcategories.json', 'w', encoding='utf-8') as file:
		    json.dump(sub_categories, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    get_category_ids()