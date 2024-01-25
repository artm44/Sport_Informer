from datetime import datetime
from aiogram import  Router, types
from aiogram.utils.markdown import hitalic, hbold, hlink

from parsers.flash_score import getInfo
from parsers.models import filter_games
from parsers.vk import getBroadcastLink, getVideos

messages_router = Router()

@messages_router.message()
async def info_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    games = await getInfo(message.text)
    if len(games) == 0:
        await message.answer("Такой команды или спортсмена не найдено!\nПопробуйте снова")
        return
    
    videos = await getVideos(games[0].sport)
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
            link = await getBroadcastLink(team1=game.player1, team2=game.player2, items=videos)
            if not link is None:
                answer += " " + hlink("ССЫЛКА", link)
        answer += "\n"
    await message.answer(text=answer)