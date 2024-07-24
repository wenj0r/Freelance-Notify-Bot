import requests
from config import TOKEN, USERS

json_data = {'chat_id': USERS[0],
             'text': 'ahahhaha',
             'parse_mode': 'HTML',
             'link_preview_options': {'is_disabled': True}}

url = 'https://api.telegram.org/bot'+TOKEN+'/sendMessage'

resp = requests.post(url, json=json_data)
print(resp.text)