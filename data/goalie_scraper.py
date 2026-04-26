import requests
from bs4 import BeautifulSoup

URL = "https://www.dailyfaceoff.com/starting-goalies/"


def get_goalies():
    try:
        r = requests.get(URL, timeout=10)

        if r.status_code != 200:
            return {}

        soup = BeautifulSoup(r.text, "html.parser")

        cards = soup.select(".starting-goalies-card")

        goalies = {}

        for c in cards:
            try:
                teams = c.select(".team-name")
                names = c.select(".goalie-name")

                goalies[teams[0].text.strip()] = names[0].text.strip()
                goalies[teams[1].text.strip()] = names[1].text.strip()
            except:
                continue

        return goalies

    except:
        return {}