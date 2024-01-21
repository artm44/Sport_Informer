from urllib.parse import urlencode
import requests
import json

def getUrlParams(team: str) -> (bool, str, str, str):
    param = urlencode({'q': team})

    url = f"https://s.livesport.services/api/v2/search/?{param}&lang-id=12&type-ids=1,2,3,4&project-id=46&project-type-id=1"

    response = requests.get(url=url)
    if response.text == "[]":
        return False, "", "", "" 
    return True, json.loads(response.text)[0]['type']['name'].lower(), json.loads(response.text)[0]['url'], json.loads(response.text)[0]['id']


def main():
    print(getUrlParams('медвдв'))

if __name__ == '__main__':
    main()