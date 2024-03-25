from datetime import datetime

from parsers.models import Info, SPORTS_BY_ID, IMPORTANT_TOURNAMENTS


def filter_games(games: list[Info], results: int, presents: int) -> list[Info]:
    """
    Filtering games:
    """
    today = datetime.now()
    ind = 0
    for game in games:
        if game.date > today:
            break
        ind += 1

    return games[0 if (ind - results) < 0 else (ind - results): ind] \
        + games[ind: len(games) if (ind + presents) > len(games) else (ind + presents)]
