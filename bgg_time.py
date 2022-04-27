import os
import sys
from bs4 import BeautifulSoup

import bgg_core


def get_plays(id):
    """Get plays for game with given id."""

    query_dict = {"id": id}
    page = 1
    more_pages = True
    plays = {}

    while more_pages:

        more_pages = False

        query_dict["page"] = page
        response = bgg_core.get_data("plays", query_dict)
        soup = BeautifulSoup(response, "xml")

        for tag in soup.find_all("play"):
            play_dict = {}
            play_dict["userid"] = tag["userid"]
            play_dict["date"] = tag["date"]
            play_dict["length"] = int(tag["length"])
            play_dict["quantity"] = int(tag["quantity"])
            play_dict["players"] = int(len(tag.find_all("player")))
            plays[tag["id"]] = play_dict
            more_pages = True

        print("Parsed page %s for game id %s" % (page, id))

        page += 1

    return plays


def main():
    """Analyze length of time for logged plays of game."""

    # Ask for game to analyze.
    search = input("Enter board game to search (leave empty if finished):")

    matches = bgg_core.find_game(search)

    print("Games found:")
    for game_id, name in matches.items():
        print(game_id + "\t" + name)
    game_id = input("Enter the number before the intended game:")
    name = matches[game_id]

    players = input("Enter player count by which to filter (default is all counts):")

    print("Analyzing logged play times:")

    print(name)

    plays = {}
    filename = "plays/%s.json" % game_id

    if os.path.exists(filename):
        plays = bgg_core.read_data(filename)
    else:
        plays = get_plays(game_id)
        bgg_core.write_data(plays, filename)

    timed_plays = [p for p in plays.values() if p["length"]]
    if players:
        timed_plays = [p for p in timed_plays if p["players"] == int(players)]
    time = sum(p["length"] for p in timed_plays)
    num_plays = sum(p["quantity"] for p in timed_plays)
    print("Timed plays: %d" % num_plays)
    avg_time = float(time) / num_plays
    print("Average time: %.2f" % avg_time)


if __name__ == "__main__":
    main()
