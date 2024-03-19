from dataclasses import dataclass, field
from datetime import datetime

from aiogram.utils.markdown import hbold, hunderline

SPORTS = {'football': 1, 'tennis': 2, 'basketball': 3, 'hockey': 4, 'volleyball': 12}
SPORTS_BY_ID = {1: 'football', 2: 'tennis', 3: 'basketball', 4: 'hockey', 12: 'volleyball'}


@dataclass
class GameInfo:
    date: datetime
    tournament: str
    player1: str
    player2: str
    score1: int
    score2: int
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


async def filter_games(games: list[GameInfo], results: int, presents: int) -> list[GameInfo]:
    """
    Filtering games: 
    """
    today = datetime.now()
    ind = 0
    for game in games:
        if game.date > today:
            break
        else:
            ind += 1

    return games[0 if (ind - results) < 0 else (ind - results): ind] \
        + games[ind: len(games) if (ind + presents) > len(games) else (ind + presents)]
