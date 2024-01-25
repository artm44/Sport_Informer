import asyncio
import aiohttp
import re
import json

from datetime import datetime
from typing import List
from urllib.parse import urlencode

from parsers.models import GameInfo

HEADERS = {"X-Fsign": "SW9D1eZo"}

async def getUrlParams(team: str) -> list[str] | None:
    """
    Returns url parameters for the team results url-page
    Args:
        team (str): sport team

    Returns:
        list[str] | None: list with url parameters
    """
    param = urlencode({'q': team})
    url = f"https://s.livesport.services/api/v2/search/?{param}&lang-id=12&type-ids=1,2,3,4&project-id=46&project-type-id=1"

    async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                text = await response.text() 

    if text == "[]":
        return None
    
    data = json.loads(text)[0]
    return [data['type']['name'].lower(), data['url'], data['id']]

async def getInfo(name: str) -> list[GameInfo]:
    """
    Returns information (results, fixtures) about team
    Args:
        name (str): name of team

    Returns:
        list[GameInfo]: list with games 
    """
    response = await getUrlParams(name)
    if response is None:
        return []
    
    url_params = response
    url = f"https://www.flashscorekz.com/{url_params[0]}/{url_params[1]}/{url_params[2]}/"

    async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response_text = await response.text()

    text = re.findall(r'summary-[results, fixtures].*\n.*`(SA.*)' , response_text)

    if len(text) == 0:
        return []
    
    sport_id = int(re.search(r'sport=(\d+)' , response_text).group(1))

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
    """ 
    Returns the shedule 

    Args:
        sport_id (int): sport
        date (int, optional): difference of a day from today. Defaults to 0.

    Returns:
        list[GameInfo]: list with games
    """
    url = f"https://local-ruua.flashscore.ninja/46/x/feed/f_{sport_id}_{date}_3_ru-kz_1"

    async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=HEADERS) as response:
                text = await response.text()

    data_list = [{}]
    data = text.split('¬')
    for item in data:
        key, value = item.split('÷')[0], item.split('÷')[-1]
        if '~' in item:
            data_list.append({key: value})
        else:
            data_list[-1].update({key: value})    

    games = []
    tournament = None
    is_important = False
    for item in data_list:
        if '~ZA' in list(item.keys())[0]: #tournament
            tournament = item.get('~ZA')
            if item.get('ZD') == 't':
                is_important = True
            else:
                is_important = False
            continue

        if not is_important:
            continue

        if '~AA' not in list(item.keys())[0]: #game
            continue
        
        date = datetime.fromtimestamp(int(item.get('AD')))
        player1 = item.get('AE')
        player2 = item.get('AF')
        score1 = item.get('AG')
        score2 = item.get('AH')
        status = True if item.get('AN') == "y" else False

        games.append(GameInfo(date, tournament, player1, player2, score1, score2, sport_id, status))
    return games


def main():
    #name = input("Введите имя команды:")
    #games = asyncio.run(getInfo(name))
    games = asyncio.run(getShedule(1))
    for game in games:
        print(game)

if __name__ == "__main__":
    main()