import json
import os
import time
import requests
from bs4 import BeautifulSoup

base_url = "https://www.boardgamegeek.com/xmlapi2"


def pager(data="thing", query_dict={}, max_retry=1):
    page = 1
    retries = 0
    ratings = {}

    while retries < max_retry:

        time.sleep(retries)
        retries += 1
        query_dict["page"] = page
        response = get_data(data, query_dict)
        soup = BeautifulSoup(response, "xml")

        if not soup.find_all("error"):
            page += 1
            retries = 0
            yield page, soup


def get_games_by_rank_page(page):
    """Scrape all games from page of rankings."""
    url = "https://boardgamegeek.com/browse/boardgame/page/"
    url = "/".join([url, str(page)])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Iterate over all non-header rows
    for row in soup.find_all("tr")[1:]:
        tag = row.find(attrs={"class": "primary"})
        name = tag.string
        game_id = tag.attrs["href"].split("/")[2]
        yield game_id, name


def get_username(userid):
    """Get username from id."""
    url = "https://boardgamegeek.com/trade/feedback"
    url = "/".join([url, str(userid)])
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    tag = soup.find(attrs={"data-userid": str(userid)})
    return tag.attrs["data-username"]


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
        for _ in range(5):
            records = func(id)
            if records:
                break
        write_data(records, filename)
        return records
