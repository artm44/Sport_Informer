import asyncio
import requests
import json
import os

from dotenv import load_dotenv



with open('parsing/vk_groups.json') as f:
    file_content = f.read()
    templates = json.loads(file_content)


load_dotenv()
TOKEN = os.getenv('VK_TOKEN')


async def getVideos(sport: str, count: int=10) -> [{}]:
    url = 'https://api.vk.com/method/video.get'
    groups = templates[sport]['groups']
    videos = []
    for group in groups:
        params = {
            'access_token': TOKEN,
            'v': '5.131',
            'owner_id': group['id'],
            'count' : count
        }
        response = requests.get(url, params)
        data = response.json()
        if 'response' in data:
            videos.append({'group_url': group['url'], 'videos': data['response']['items']})
    return videos

async def getBroadcastLink(team1: str, team2: str, items: [{}]) -> str:
    for item in items:
        group_url = item['group_url']
        videos = item['videos']
        for video in videos:
            title = video['title']
            if (team1.split()[0] in title or team2.split()[0] in title) and video.get('live_status') == 'started':
                return f"{group_url}?z=video{video['owner_id']}_{video['id']}"
    return ""


def main():
    data = input("Введите название спорта, имя команды1, имя команды2:").split()
    videos = asyncio.run(getVideos(data[0]))
    link = asyncio.run(getBroadcastLink(data[1], data[2], videos))
    print(link)

if __name__ == "__main__":
    main()