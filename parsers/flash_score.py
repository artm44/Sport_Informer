import asyncio
import aiohttp
import re
import json

from datetime import datetime
from urllib.parse import urlencode

from parsers.models import GameInfo
from database.redis_utils import get_from_redis, set_to_redis

HEADERS = {"X-Fsign": "SW9D1eZo"}


async def get_url_params(team: str) -> list[str] | None:
    """
    Returns url parameters for the team results url-page
    Args:
        team (str): sport team

    Returns:
        list[str] | None: list with url parameters
    """
    param = urlencode({'q': team})
    url = (f"https://s.livesport.services/api/v2/search/?{param}&lang-id=12&type-ids=1,2,3,"
           f"4&project-id=46&project-type-id=1")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            text = await response.text()

    if text == "[]":
        return None

    data = json.loads(text)[0]
    return [data['type']['name'].lower(), data['url'], data['id']]


async def get_info(name: str) -> list[GameInfo]:
    """
    Returns information (results, fixtures) about team
    Args:
        name (str): name of team

    Returns:
        list[GameInfo]: list with games 
    """
    response = await get_url_params(name)
    if response is None:
        return []

    hash_name = f"url_{response[2]}"
    value: str = await get_from_redis(hash_name)

    if value is not None:
        games = json.loads(value)
        return [GameInfo.from_json(json.loads(game)) for game in games]

    url_params = response
    url = f"https://www.flashscorekz.com/{url_params[0]}/{url_params[1]}/{url_params[2]}/"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response_text = await response.text()

    text = re.findall(r'summary-[results, fixtures].*\n.*`(SA.*)', response_text)

    if len(text) == 0:
        return []

    sport_id = int(re.search(r'sport=(\d+)', response_text).group(1))

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

    games: list[GameInfo] = []
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

        games.append(GameInfo(date=date, tournament=tournament, player1=player1, player2=player2,
                              score1=score1, score2=score2, status=status, sport_id=sport_id))

    games = sorted(games, key=lambda game: game.date)

    games_json = [game.to_json() for game in games]
    await set_to_redis(hash_name, json.dumps(games_json), 60)

    return games


async def get_schedule(sport_id: int, date: int = 0) -> list[GameInfo]:
    """ 
    Returns the schedule of the sport
    Args:
        sport_id (int): sport
        date (int, optional): difference of a day from today. Defaults to 0.

    Returns:
        list[GameInfo]: list with games
    """
    hash_name = f"schedule_{sport_id}_{date}"
    value: str = await get_from_redis(hash_name)

    if value is not None:
        games = json.loads(value)
        return [GameInfo.from_json(json.loads(game)) for game in games]

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
        if '~ZA' in list(item.keys())[0]:  # tournament
            tournament = item.get('~ZA')
            if item.get('ZD') == 't':
                is_important = True
            else:
                is_important = False
            continue

        if not is_important:
            continue

        if '~AA' not in list(item.keys())[0]:  # game
            continue

        date = datetime.fromtimestamp(int(item.get('AD')))
        player1 = item.get('AE')
        player2 = item.get('AF')
        score1 = item.get('AG')
        score2 = item.get('AH')
        status = True if item.get('AN') == "y" else False

        games.append(GameInfo(date=date, tournament=tournament, player1=player1, player2=player2,
                              score1=score1, score2=score2, status=status, sport_id=sport_id))

    games_json = [game.to_json() for game in games]
    await set_to_redis(hash_name, json.dumps(games_json), 60)

    return games


def main():
    # name = input("Введите имя команды:")
    # games = asyncio.run(getInfo(name))
    games = asyncio.run(get_schedule(1))
    for game in games:
        print(game)


if __name__ == "__main__":
    main()
