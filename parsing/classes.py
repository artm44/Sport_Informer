from datetime import datetime

from aiogram.utils.markdown import hbold, hunderline

SPORTS = {'football': 1,  'tennis': 2,'basketball': 3, 'hockey': 4,'volleyball': 12 }

class GameInfo:
    def __init__(self, date: datetime, tournament: str, player1: str, player2: str, score1: int, score2: int, sport_id: int, status: bool) -> None:
        self.date = date
        self.tournament = tournament
        self.player1 = player1
        self.player2 = player2
        self.score1 = score1
        self.score2 = score2
        self.sport = None
        for key in SPORTS:
            if SPORTS[key] == sport_id:
                self.sport = key
                break
        self.status = status

    def __str__(self):
        game_status = "LIVE" if self.status  else ""
        score1 = "" if self.score1 is None else str(self.score1)
        score2 = "" if self.score2 is None else str(self.score2)
        date = self.date.strftime("%d.%m.%Y %H:%M")
        return f"{self.sport} {hunderline(date)} {self.tournament}: {hbold(self.player1)} {score1} - {score2} {hbold(self.player2)} {game_status}"
    
    def to_str(self, spec: bool=True):
        game_status = "LIVE" if self.status  else ""
        score1 = "" if self.score1 is None else str(self.score1)
        score2 = "" if self.score2 is None else str(self.score2)
        date = self.date.strftime("%d.%m.%Y %H:%M")
        tournament = self.tournament if spec is True else ""
        return f"{hunderline(date)} {tournament}: {hbold(self.player1)} {score1} - {score2} {hbold(self.player2)} {game_status}"
    

def filter_games(games: list[GameInfo], past: int, future: int) -> list[GameInfo]:
    today = datetime.now()
    ind = 0
    for game in games:
        if game.date > today:
            break
        else:
            ind += 1
    
    return games[0 if (ind - past) < 0 else (ind - past) : ind] + games[ind: len(games) if (ind + future) > len(games) else (ind + future)]
    



