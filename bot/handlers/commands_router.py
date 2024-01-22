from aiogram import  Router, types
from aiogram.filters import Command, CommandStart
from aiogram.utils.markdown import hitalic, hlink, hbold

from parsers.flash_score import getShedule
from parsers.vk import getBroadcastLink, getVideos
from parsers.models import SPORTS

commands_router = Router()

@commands_router.message(CommandStart())
async def command_start_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!\n" +
                         "Выбери команду из списка или напиши название спортивной команды или" \
                         " имя спортсмена, чтобы узнать информацию:")

@commands_router.message(Command('about'))
async def command_about_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/about` command
    """
    answer = "Выбери команду из списка меню.\n" \
            "Например, команда <i>/football</i> покажет расписание на сегодня и завтра лучших футбольных турниров.\n" \
            "Или напиши название спортивной команды или имя спортсмена, чтобы получить результаты и расписание."
    await message.answer(text=answer)

@commands_router.message(Command(*SPORTS.keys()))
async def command_sport_handler(message: types.Message) -> None:
    """
    This handler receives messages with `/some_sport` command
    """
    sport = message.text[1:]
    sport_id = SPORTS.get(sport)
    games = await getShedule(sport_id)
    videos = await getVideos(sport)
    tournament = games[0].tournament
    answer = "Расписание на сегодня\n" + hitalic(tournament) + '\n'
    for game in games:
        if tournament != game.tournament:
            tournament = game.tournament
            answer += hitalic(tournament) + '\n'
        answer += "• " + game.to_str(False)
        if game.status:
            link = await getBroadcastLink(team1=game.player1, team2=game.player2, items=videos)
            if len(link) != 0:
                answer += " " + hlink("ССЫЛКА", link)
        answer += "\n"
    await message.answer(text=answer)

    games = await getShedule(sport_id, 1)
    tournament = games[0].tournament
    answer = "Расписание на завтра\n" + hitalic(tournament) + '\n'
    for game in games:
        if tournament != game.tournament:
            tournament = game.tournament
            answer += hitalic(tournament) + '\n'
        answer = answer + "• " + game.to_str(False) + "\n"
    
    await message.answer(text=answer)