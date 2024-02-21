import glob
import os
from datetime import datetime

import bgg_core


def get_plays(id):
    """Get plays for game with given id."""

    query_dict = {"id": id, "pagesize": 100}

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
            yield tag["id"], play_dict
            more_pages = True

        print("Parsed plays page %s for game id %s" % (page, id))


def play_stats(game_id, players=None, time_limit=500, play_limit=100, update=False):
    """Calculate play stats."""
    plays = bgg_core.read_data(game_id, "plays", get_plays, update=update)

    with bgg_core.PersistDict("yearpublished.json", bgg_core.get_game_year) as games:
        yr_published = int(games[game_id])

    plays_count = 0
    users = []
    user_years = []
    user_year_plays_count = 0
    time_sum = 0
    timed_plays_count = 0
    timed_users = []
    for play in plays.values():
        if play["quantity"] < play_limit:
            plays_count += play["quantity"]
            users.append(play["userid"])

            try:
                yr = datetime.strptime(play["date"], "%Y-%m-%d").year
                if yr >= yr_published:
                    user_years.append((yr, play["userid"]))
                    user_year_plays_count += play["quantity"]
            except ValueError:
                pass

            if 0 < play["length"] < time_limit:
                if players and (int(players) != play["players"]):
                    continue
                time_sum += play["length"]
                timed_plays_count += play["quantity"]
                timed_users.append(play["userid"])

    users_count = len(set(users))
    avg_plays = plays_count / users_count
    user_years_count = len(set(user_years))
    avg_plays_per_yr = user_year_plays_count / user_years_count
    timed_users_count = len(set(timed_users))
    avg_time = float(time_sum) / timed_plays_count
    avg_time_per_user = float(time_sum) / timed_users_count

    return {
            "plays_count": plays_count,
            "users_count": users_count,
            "avg_plays": avg_plays,
            "avg_plays_per_yr": avg_plays_per_yr,
            "time_sum": time_sum,
            "timed_plays_count": timed_plays_count,
            "timed_users_count": timed_users_count,
            "avg_time": avg_time,
            "avg_time_per_user": avg_time_per_user
            }


def all_play_stats():
    """Get all downloaded play stats."""
    games_dict = {}
    for f in glob.glob("plays/*.json"):
        game_id = os.path.basename(os.path.splitext(f)[0])
        games_dict[game_id] = play_stats(game_id)
    return games_dict


def main():
    """Analyze length of time for logged plays of game."""

    # Ask for game to analyze.
    game_id, name = bgg_core.select_game()

    players = input("Enter player count by which to filter (default is all counts):")

    print("Analyzing logged play times:")

    print(name)

    game_stats = play_stats(game_id, players, update=True)
    print("Timed plays: %d" % game_stats["timed_plays_count"])
    print("Average time: %.2f" % game_stats["avg_time"])


if __name__ == "__main__":
    main()
