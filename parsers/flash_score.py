import asyncio
import aiohttp
import json

from urllib.parse import urlencode

from parsers.models import Info, SPORTS_BY_ID, InfoFactory
from database.redis_utils import get_from_redis, set_to_redis

HEADERS = {"X-Fsign": "SW9D1eZo"}


async def get_url_params(team: str) -> tuple[dict, int] | None:
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
    url_info = {
        'type': data['type']['name'].lower(),
        'url': data['url'],
        'id': data['id']
    }
    return url_info, int(data['sport']['id'])


async def get_info(name: str) -> list[Info]:
    """
    Returns information (results, fixtures) about team
    Args:
        name (str): name of team

    Returns:
        list[GameInfo]: list with games 
    """
    # Находим параметры для получения данных
    response = await get_url_params(name)
    if response is None:
        return []

    url_params, sport_id = response

    # Проверка на возможность обработки такого вида спорта
    if sport_id not in SPORTS_BY_ID.keys():
        return []

    # Получаем нужную реализацию класса
    info_class_ = InfoFactory.get(SPORTS_BY_ID[sport_id])

    # Поиск данных в Редис
    hash_name = f"url_{url_params['id']}"
    value: str = await get_from_redis(hash_name)
    if value is not None:
        games_json = json.loads(value)
        return [info_class_.from_json(json.loads(game)) for game in games_json]

    # Получаем данные из интернета
    url = info_class_.get_url(url_params, url_params['type'])
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            response_text = await response.text()

    data_list = info_class_.parse_text(response_text, url_params['type'])

    games: list[Info] = info_class_.parse_data(data_list, sport_id, url_params['type'])

    games = sorted(games, key=lambda game: game.date)

    # Запись данных в Редис
    games_json = [game.to_json() for game in games]
    await set_to_redis(hash_name, json.dumps(games_json), 60)

    return games


async def get_schedule(sport_id: int, date: int = 0) -> list[Info]:
    """ 
    Returns the schedule of the sport
    Args:
        sport_id (int): sport
        date (int, optional): difference of a day from today. Defaults to 0.

    Returns:
        list[GameInfo]: list with games
    """
    # Получаем нужную реализацию класса
    info_class_ = InfoFactory.get(SPORTS_BY_ID[sport_id])

    # Поиск данных в Редис
    hash_name = f"schedule_{sport_id}_{date}"
    value: str = await get_from_redis(hash_name)
    if value is not None:
        games = json.loads(value)
        return [info_class_.from_json(json.loads(game)) for game in games]

    # Получаем данные из интернета
    url = info_class_.get_url({'id': sport_id, 'date': date}, 'schedule')

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=HEADERS) as response:
            response_text = await response.text()

    data_list = info_class_.parse_text(response_text, 'schedule')

    games: list[Info] = info_class_.parse_data(data_list, sport_id, 'schedule')

    # Запись данных в Редис
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
