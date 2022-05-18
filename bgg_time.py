import bgg_core


def get_plays(id):
    """Get plays for game with given id."""

    query_dict = {"id": id, "pagesize": 100}
    plays = {}

    for page, soup in bgg_core.pager("plays", query_dict, 3):

        tags = soup.find_all("play")
        if not tags:
            break
        for tag in tags:
            play_dict = {}
            play_dict["userid"] = tag["userid"]
            play_dict["date"] = tag["date"]
            play_dict["length"] = int(tag["length"])
            play_dict["quantity"] = int(tag["quantity"])
            play_dict["players"] = int(len(tag.find_all("player")))
            plays[tag["id"]] = play_dict
            more_pages = True

        print("Parsed plays page %s for game id %s" % (page, id))

    return plays


def main():
    """Analyze length of time for logged plays of game."""

    # Ask for game to analyze.
    game_id, name = bgg_core.select_game()

    players = input("Enter player count by which to filter (default is all counts):")

    print("Analyzing logged play times:")

    print(name)

    plays = bgg_core.read_data(game_id, "plays", get_plays)

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
