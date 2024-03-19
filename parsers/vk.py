import asyncio
import aiohttp
import json

from config import VK_TOKEN

with open('parsers/vk_groups.json') as f:
    file_content = f.read()
    templates = json.loads(file_content)


async def get_videos(sport: str, count: int = 10) -> [{}]:
    """
    Returns list of videos for some sport from vk groups
    Returns:
        _type_: _description_
    """
    url = 'https://api.vk.com/method/video.get'
    try:
        groups = templates[sport]['groups']
    except KeyError:
        return []
    videos = []
    for group in groups:
        params = {
            'access_token': VK_TOKEN,
            'v': '5.131',
            'owner_id': group['id'],
            'count': count
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, params=params, ssl=False) as response:
                    data = await response.json()
            except:
                return []
        if 'response' in data:
            videos.append({'group_url': group['url'], 'videos': data['response']['items']})
    return videos


async def get_broadcast_link(team1: str, team2: str, items: [{}]) -> str | None:
    """
    Filters incoming videos and returns a link to the match broadcast
    Args:
        team1 (str): team1
        team2 (str): team2
        items (_type_): videos for filtering

    Returns:
        str | None : broadcast link
    """
    for item in items:
        group_url = item['group_url']
        videos = item['videos']
        for video in videos:
            title = video['title']
            if (team1.split()[0] in title or team2.split()[0] in title) and video.get('live_status') == 'started':
                return f"{group_url}?z=video{video['owner_id']}_{video['id']}"
    return None


def main():
    data = input("Введите название спорта, имя команды1, имя команды2:").split()
    videos = asyncio.run(get_videos(data[0]))
    for video in videos:
        print(video)
    link = asyncio.run(get_broadcast_link(data[1], data[2], videos))
    print(link)


if __name__ == "__main__":
    main()
