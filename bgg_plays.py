import collections
import glob
import json
import os

import bgg_core
import bgg_compare
import bgg_time


def get_user_plays(game_id):
    """Get game ratings and plays per user."""

    ratings = bgg_core.read_data(game_id, "ratings", bgg_compare.get_ratings)

    plays = bgg_core.read_data(game_id, "plays", bgg_time.get_plays)

    userid_plays = collections.defaultdict(int)
    for play_dict in plays.values():
        userid_plays[play_dict["userid"]] += play_dict["quantity"]

    user_plays = {}
    total_users = len(userid_plays)
    user_num = 0

    with bgg_core.PersistDict("users.json", bgg_core.get_username) as users:
        for userid, plays in userid_plays.items():
            user_num += 1
            if not user_num % 50:
                print("Parsed %d of %d users for game id %s" % (user_num, total_users, game_id))
            username = users[userid]
            try:
                user_plays[username] = {"rating": ratings[username], "plays": plays}
            except KeyError:
                pass

    return user_plays


def user_play_stats(game_id):
    """Rate game, weighting each user's rating by number of plays."""
    user_plays = bgg_core.read_data(game_id, "user_plays", get_user_plays)

    rating_sum = 0
    plays_count = 0
    users_count = len(user_plays)
    for play_dict in user_plays.values():
        rating_sum += float(play_dict["rating"]) * play_dict["plays"]
        plays_count += play_dict["plays"]

    avg_plays = plays_count / users_count
    play_rating = rating_sum / plays_count

    return {
            "rated_plays_count": plays_count,
            "rated_users_count": users_count,
            "rated_avg_plays": avg_plays,
            "rated_play_weighted_rating": play_rating
            }


def all_user_play_stats():
    """Get all downloaded user play stats."""
    games_dict = {}
    for f in glob.glob("user_plays/*.json"):
        game_id = os.path.basename(os.path.splitext(f)[0])
        games_dict[game_id] = user_play_stats(game_id)
    return games_dict


def main(game_id, name):
    """Print user play stats."""


    print(name)

    game_stats = user_play_stats(game_id)

    print("Plays for %s: %d" % (name, game_stats["rated_plays_count"]))
    print("Unique users: %d" % game_stats["rated_users_count"])
    print("Avg. plays: %.2f" % game_stats["rated_avg_plays"])
    print("Weighted play rating: %.2f" % game_stats["rated_play_weighted_rating"])


if __name__ == "__main__":
    # Ask for game to analyze.
    try:
        game_id, name = bgg_core.select_game()
        main(game_id, name)

    # If no games entered, compare all downloaded game stats.
    except ValueError:
        with bgg_core.PersistDict("games.json", bgg_core.get_game_name) as games:
            for f in glob.glob("user_plays/*.json"):
                game_id = os.path.basename(os.path.splitext(f)[0])
                name = games[game_id]
                main(game_id, name)
