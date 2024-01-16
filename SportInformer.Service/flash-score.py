import requests
from datetime import datetime
import re
from find import getUrlParams
import json

headers = {"X-Fsign": "SW9D1eZo"}
url_params = getUrlParams(input("Введите название команды/игрока:"))
url = f"https://www.flashscorekz.com/{url_params[0]}/{url_params[1]}/{url_params[2]}/"
response = requests.get(url=url, headers=headers)

text = re.findall(r'`SA.*' , response.text)



data_list = [{}]
for txt in text:
    data = txt.split('¬')
    for item in data:
        key, value = item.split('÷')[0], item.split('÷')[-1]
        if '~' in item:
            data_list.append({key: value})
        else:
            data_list[-1].update({key: value})

tournament = None
for item in data_list:
    if '~ZA' in list(item.keys())[0]:
        tournament = item.get('~ZA').split(':')[1:][0]
    if '~AA' not in list(item.keys())[0]:
        continue
    date = datetime.fromtimestamp(int(item.get('AD')))
    player1 = item.get('AE')
    player2 = item.get('AF')
    score1 = item.get('AG')
    score2 = item.get('AH')
    status = "LIVE" if item.get('AN') == "y" else "Завершён"

    print(date, tournament, ':', player1, score1, ':', score2, player2, status)
