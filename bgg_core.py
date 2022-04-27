import json
import os
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


def select_game():
    """Ask for game to analyze."""

    search = input("Enter board game to search (leave empty if finished):")

    if not search:
        raise ValueError

    matches = find_game(search)

    print("Games found:")
    for id, name in matches.items():
        print(id + "\t" + name)
    game_id = input("Enter the number before the intended game:")
    name = matches[game_id]

    return game_id, name


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


def read_data(id, dir, func):
    """Read data into dict."""

    filename = "%s/%s.json" % (dir, id)

    if os.path.exists(filename):
        with open(filename) as jsonfile:
            return json.load(jsonfile)
    else:
        os.makedirs(dir, exist_ok=True)
        records = func(id)
        write_data(records, filename)
        return records
