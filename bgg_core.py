import json
import requests
from bs4 import BeautifulSoup

base_url = "https://www.boardgamegeek.com/xmlapi2"


def get_data(base_type, params):
    """Download data from BGG API."""

    url = "/".join([base_url, base_type])
    response = requests.get(url, params)
    return response.text


def find_game(search):
    """Search for game matches."""

    query_dict = {"type": "boardgame", "query": search}
    response = get_data("search", query_dict)
    soup = BeautifulSoup(response, "xml")

    matches = {}

    for tag in soup.find_all("item"):
        id = tag["id"]
        name = tag.contents[1]["value"]
        matches[id] = name

    return matches


def get_game_info(id_list):
    """Get game info from ids."""

    ids = ",".join(id_list)
    query_dict = {"id": ids, "type": "boardgame"}
    response = get_data("thing", query_dict)
    soup = BeautifulSoup(response, "xml")

    games = []

    for id in id_list:
        tag = soup.find("item", attrs={"id": id})
        games.append(tag)

    return games


def write_data(data_dict, filename):
    """Save dict to reduce repetitive scraping."""

    with open(filename, "w") as jsonfile:

        json.dump(data_dict, jsonfile)


def read_data(filename):
    """Read data into dict."""

    with open(filename) as jsonfile:

        return json.load(jsonfile)
