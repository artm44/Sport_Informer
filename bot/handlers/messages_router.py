from datetime import datetime
from aiogram import Router, types
from aiogram.utils.markdown import hitalic, hbold, hlink

from parsers.flash_score import get_info
from parsers.models import filter_games
from parsers.vk import get_broadcast_link, get_videos

messages_router = Router()


@messages_router.message()
async def info_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    games = await get_info(message.text)
    if len(games) == 0:
        await message.answer("Такой команды или спортсмена не найдено!\nПопробуйте снова")
        return

    videos = await get_videos(games[0].sport)
    games = await filter_games(games, 4, 3)

    tournament = ""

    today = datetime.now()
    answer = f"{hbold("Результаты")}:\n" if games[0].date < today else ""
    flag = True
    for game in games:
        if flag and game.date > today:
            answer += f"\n{hbold("Предстоящие матчи")}:\n"
            flag = False
            tournament = ""
        if tournament != game.tournament:
            tournament = game.tournament
            answer += hitalic(tournament) + "\n"
        answer += "• " + game.to_str(False)
        if game.status:
            link = await get_broadcast_link(team1=game.player1, team2=game.player2, items=videos)
            if link is not None:
                answer += " " + hlink("ССЫЛКА", link)
        answer += "\n"
    await message.answer(text=answer)
