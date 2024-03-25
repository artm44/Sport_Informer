import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
import json

from aiogram.utils.markdown import hbold, hunderline

SPORTS = {'football': 1, 'tennis': 2, 'basketball': 3, 'hockey': 4, 'volleyball': 12, 'formula1': 32}
SPORTS_BY_ID = {1: 'football', 2: 'tennis', 3: 'basketball', 4: 'hockey', 12: 'volleyball', 32: 'formula1'}

IMPORTANT_TOURNAMENTS = {
    'football': [],
    'tennis': ['ATP - ОДИНОЧНЫЙ РАЗРЯД', 'WTA - ОДИНОЧНЫЙ РАЗРЯД'],
    'basketball': [],
    'hockey': [],
    'volleyball': []
}

SPORT_CLASSES = {
    'GameInfo': [1, 2, 3, 4, 12],
    'RaceInfo': [32]
}


def is_important_tournament(tournament: str, sport_id: int) -> bool:
    sport = SPORTS_BY_ID[sport_id]
    for pattern in IMPORTANT_TOURNAMENTS[sport]:
        if pattern in tournament:
            return True
    return False

class Info(ABC):
    @abstractmethod
    def to_str(self):
        ...

    @abstractmethod
    def to_json(self):
        ...

    @classmethod
    @abstractmethod
    def from_json(cls, json_data):
        ...

    @classmethod
    @abstractmethod
    def get_url(cls, url_params: dict, type_info: str) -> str:
        ...

    @classmethod
    @abstractmethod
    def parse_text(cls, text: str, type_info: str) -> list[dict]:
        ...

    @classmethod
    @abstractmethod
    def parse_data(cls, data: list[dict], sport_id: int, type_info: str) -> list:
        ...


@dataclass
class GameInfo(Info):
    date: datetime
    tournament: str
    player1: str
    player2: str
    score1: str
    score2: str
    status: bool
    sport_id: int = field(repr=False)
    sport: str = None

    def __post_init__(self):
        self.sport = SPORTS_BY_ID.get(self.sport_id, '')

    def to_str(self, spec: bool = True):
        game_status = "LIVE" if self.status else ""
        score1 = "" if self.score1 is None else self.score1
        score2 = "" if self.score2 is None else self.score2
        date = self.date.strftime("%d.%m.%Y %H:%M")
        tournament = self.tournament if spec else ""
        return f"{hunderline(date)} {tournament}: {hbold(self.player1)} {score1} - \
{score2} {hbold(self.player2)} {game_status}"

    def to_json(self):
        game_dict = self.__dict__.copy()
        game_dict['date'] = str(game_dict['date'])
        return json.dumps(game_dict)

    @classmethod
    def from_json(cls, json_data):
        json_data['date'] = datetime.strptime(json_data['date'], '%Y-%m-%d %H:%M:%S')
        return cls(**json_data)

    @classmethod
    def get_url(cls, url_params: dict, type_info: str) -> str:
        if type_info != 'schedule':
            return f"https://www.flashscorekz.com/{url_params['type']}/{url_params['url']}/{url_params['id']}/"
        return f"https://local-ruua.flashscore.ninja/46/x/feed/f_{url_params['id']}_{url_params['date']}_3_ru-kz_1"

    @classmethod
    def parse_text(cls, text: str, type_info: str) -> list[dict]:
        if type_info != 'schedule':
            text = re.findall(r'summary-[results, fixtures].*\n.*`(SA.*)', text)
            if len(text) == 0:
                return []
        else:
            text = [text]

        data_list = [{}]
        for txt in text:
            data = txt.split('¬')
            for item in data:
                key, value = item.split('÷')[0], item.split('÷')[-1]
                if '~' in item:
                    data_list.append({key: value})
                else:
                    data_list[-1].update({key: value})

        return data_list

    @classmethod
    def parse_data(cls, data: list[dict], sport_id: int, type_info: str) -> list:
        games: list[GameInfo] = []
        tournament = None
        is_important = True
        for item in data:
            if '~ZA' in list(item.keys())[0]:
                tournament = item.get('~ZA')
                if type_info == 'schedule':
                    if item.get('ZD', '') == 't' or is_important_tournament(tournament, sport_id):
                        is_important = True
                    else:
                        is_important = False
                    continue
            if not is_important:
                continue
            if '~AA' not in list(item.keys())[0]:
                continue

            date = datetime.fromtimestamp(int(item.get('AD')))
            player1 = item.get('AE', '')
            player2 = item.get('AF', '')
            score1 = item.get('AG', '')
            score2 = item.get('AH', '')
            status = True if item.get('AN', '') == "y" else False

            games.append(GameInfo(date, tournament, player1, player2, score1, score2, status, sport_id))

        return games


@dataclass
class RaceInfo(Info):
    date: datetime
    tournament: str
    player: str
    place: str
    gap: str
    status: bool
    sport_id: int = field(repr=False)
    sport: str = None

    def __post_init__(self):
        self.sport = SPORTS_BY_ID.get(self.sport_id, '')

    def to_json(self):
        game_dict = self.__dict__.copy()
        game_dict['date'] = str(game_dict['date'])
        return json.dumps(game_dict)

    @classmethod
    def from_json(cls, json_data):
        json_data['date'] = datetime.strptime(json_data['date'], '%Y-%m-%d %H:%M:%S')
        return cls(**json_data)

    def to_str(self, spec: bool = True):
        race_status = "LIVE" if self.status else ""
        place = self.place
        gap = self.gap if self.gap != '+0.000' else ''
        date = self.date.strftime("%d.%m.%Y %H:%M")
        tournament = self.tournament if spec else ""
        return f"{hunderline(date)} {tournament}: {hbold(place)} {gap} {race_status}"

    @classmethod
    def get_url(cls, url_params: dict, type_info: str) -> str:
        if type_info != 'schedule':
            return f"https://local-ruua.flashscore.ninja/46/x/feed/pe_1_3_{url_params['id']}_x"
        return f"https://local-ruua.flashscore.ninja/46/x/feed/f_{url_params['id']}_{url_params['date']}_3_ru-kz_1"

    @classmethod
    def parse_text(cls, text: str, type_info: str) -> list[dict]:
        data_list = [{}]

        data = text.split('¬')
        for item in data:
            key, value = item.split('÷')[0], item.split('÷')[-1]
            if '~' in item:
                data_list.append({key: value})
            else:
                data_list[-1].update({key: value})

        return data_list

    @classmethod
    def parse_data(cls, data: list[dict], sport_id: int, type_info: str) -> list:
        races: list[RaceInfo] = []
        tournament = ''
        is_important = True
        for item in data:
            if 'ZY' in item.keys():
                tournament = item.get('ZY')
                if type_info == 'schedule':
                    if item.get('ZD', '') == 't' or is_important_tournament(tournament, sport_id):
                        is_important = True
                    else:
                        is_important = False
                    continue
            if not is_important:
                continue
            if '~AA' not in list(item.keys())[0]:
                continue

            date = datetime.fromtimestamp(int(item.get('AD')))
            player = item.get('AD', '')
            place = item.get('WS', '')
            gap = item.get('NG', '')
            status = True if item.get('AN', '') == "y" else False

            races.append(RaceInfo(date, tournament, player, place, gap, status, sport_id))

        return races


class InfoFactory:
    @staticmethod
    def get(sport_id: int) -> Info:
        classes = {
            "GameInfo": GameInfo,
            "RaceInfo": RaceInfo
        }

        class_name = None
        for key, value in SPORT_CLASSES.items():
            if sport_id in value:
                class_name = key
                break

        class_ = classes.get(class_name, None)

        return class_
