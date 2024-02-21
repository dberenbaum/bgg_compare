import collections
import glob
import json
import os

import bgg_core
import bgg_compare
import bgg_time


def collect_game_stats(game_id):
    """Collect all game stats."""
    ratings = bgg_core.read_data(game_id, "ratings", bgg_compare.get_ratings)
    sum_rating = sum(float(r) for r in ratings.values())
    avg_rating = sum_rating / len(ratings)


    play_stats = bgg_time.play_stats(game_id)

    play_stats["avg_rating"] = avg_rating

    return play_stats


def all_games_stats():
    """Get all downloaded game stats."""
    all_ratings = bgg_compare.all_ratings()
    all_play_stats = bgg_time.all_play_stats()

    all_stats = {}
    with bgg_core.PersistDict("games.json", bgg_core.get_game_name) as games:
        for g in games.dict:
            name = games[g]
            try:
                all_stats[name] = {**all_ratings[g], **all_play_stats[g]}
            except KeyError:
                pass

    return all_stats


def print_stats(game_stats):
    """Print game stats."""
    print("Average rating: %.2f" % game_stats["avg_rating"])
    print("Plays: %d" % game_stats["plays_count"])
    print("Unique users: %d" % game_stats["users_count"])
    print("Average plays: %.2f" % game_stats["avg_plays"])
    print("Average plays per year: %.2f" % game_stats["avg_plays_per_yr"])
    print("Timed plays: %d" % game_stats["timed_plays_count"])
    print("Average time per play: %.2f" % game_stats["avg_time"])
    print("Average time per user: %.2f" % game_stats["avg_time_per_user"])
    print()


def player_count_stats(game_id, play_limit=100):
    """Calculate plays per player count."""
    plays = bgg_core.read_data(game_id, "plays", bgg_time.get_plays)

    player_count_stats = collections.defaultdict(int)
    for play in plays.values():
        if play["players"] and (play["quantity"] < play_limit):
            player_count_stats[play["players"]] += play["quantity"]

    return player_count_stats


if __name__ == "__main__":
    # Ask for game to analyze.
    try:
        game_id, name = bgg_core.select_game()
        print(name)
        game_stats = collect_game_stats(game_id)
        print_stats(game_stats)

    # If no games entered, compare all downloaded game stats.
    except ValueError:
        all_stats = all_games_stats()
        for name, game_stats in all_stats.items():
            print(name)
            print_stats(game_stats)
