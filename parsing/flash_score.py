import asyncio
import requests
from datetime import datetime
import re

from parsing.find import getUrlParams
from parsing.classes import GameInfo

HEADERS = {"X-Fsign": "SW9D1eZo"}

async def getInfo(name: str) -> list[GameInfo]:
    response = getUrlParams(name)
    if not response[0]:
        return []
    url_params = response[1:]
    url = f"https://www.flashscorekz.com/{url_params[0]}/{url_params[1]}/{url_params[2]}/"
    response = requests.get(url=url, headers=HEADERS)

    text = re.findall(r'summary-[results, fixtures].*\n.*`(SA.*)' , response.text)

    if len(text) == 0:
        return []
    
    sport_id = int(re.search(r'sport=(\d+)' , response.text).group(1))

    data_list = [{}]
    for txt in text:
        data = txt.split('¬')
        for item in data:
            key, value = item.split('÷')[0], item.split('÷')[-1]
            if '~' in item:
                data_list.append({key: value})
            else:
                data_list[-1].update({key: value})

    if len(data_list) == 0:
        return []

    games = []
    tournament = None
    for item in data_list:
        if '~ZA' in list(item.keys())[0]:
            tournament = item.get('~ZA')
        if '~AA' not in list(item.keys())[0]:
            continue
        date = datetime.fromtimestamp(int(item.get('AD')))
        player1 = item.get('AE')
        player2 = item.get('AF')
        score1 = item.get('AG')
        score2 = item.get('AH')
        status = True if item.get('AN') == "y" else False

        games.append(GameInfo(date, tournament, player1, player2, score1, score2, sport_id, status))
    games = sorted(games, key=lambda game: game.date)
    return games


async def getShedule(sport_id: int, date: int = 0) -> list[GameInfo]:
    url = f"https://local-ruua.flashscore.ninja/46/x/feed/f_{sport_id}_{date}_3_ru-kz_1"
    response = requests.get(url=url, headers=HEADERS)
    text = response.text
    data_list = [{}]
    data = text.split('¬')
    for item in data:
        key, value = item.split('÷')[0], item.split('÷')[-1]
        if '~' in item:
            data_list.append({key: value})
        else:
            data_list[-1].update({key: value})
    tournaments = []
    for item in data_list:
         if '~ZA' in list(item.keys())[0] and item.get('ZD') == 't':
             tournaments.append(item)

    games = []
    tournament = None
    is_important = False
    for item in data_list:
        if '~ZA' in list(item.keys())[0]:
            tournament = item.get('~ZA')
            if item.get('ZD') == 't':
                is_important = True
            else:
                is_important = False
        if '~AA' not in list(item.keys())[0]:
            continue
        if not is_important:
            continue
        date = datetime.fromtimestamp(int(item.get('AD')))
        player1 = item.get('AE')
        player2 = item.get('AF')
        score1 = item.get('AG')
        score2 = item.get('AH')
        status = True if item.get('AN') == "y" else False

        games.append(GameInfo(date, tournament, player1, player2, score1, score2, sport_id, status))
    #games = sorted(games, key=lambda game: game.date)
    return games


def main():
    name = input("Введите имя команды:")
    games = asyncio.run(getInfo(name))
    #games = asyncio.run(getShedule(1))
    for game in games:
        print(game)

if __name__ == "__main__":
    main()