import bgg_core
import bgg_compare


def get_num_plays(id, user):
    """Get user's num plays for game with given id."""

    query_dict = {"id": id, "username": user, "pagesize": 100}
    total_plays = 0

    for page, soup in bgg_core.pager("plays", query_dict):

        num_plays = len( soup.find_all("play"))
        if num_plays:
            total_plays += num_plays
        else:
            break

    return total_plays


def get_user_plays(game_id):
    """Get game ratings and plays per user."""

    ratings = bgg_core.read_data(game_id, "ratings", bgg_compare.get_ratings)
    total_ratings = len(ratings)

    user_plays = {}
    user_num = 0
    for user_name, rating in ratings.items():
        num_plays = get_num_plays(game_id, user_name)
        if num_plays:
            user_plays[user_name] = {"rating": rating, "plays": num_plays}
        user_num += 1
        if not user_num % 10:
            print("Parsed %d of %d users for game id %s" % (user_num, total_ratings, game_id))

    return user_plays


def main(game_id, name):
    """Rate game, weighting each user's rating by number of plays."""


    print(name)

    user_plays = bgg_core.read_data(game_id, "user_plays", get_user_plays)

    rating_sum = 0
    play_sum = 0
    total_users = len(user_plays)
    for play_dict in user_plays.values():
        rating_sum += float(play_dict["rating"]) * play_dict["plays"]
        play_sum += play_dict["plays"]

    print("Plays for %s: %d" % (name, play_sum))
    print("Unique users: %d" % total_users)
    avg_plays = play_sum / total_users
    print("Avg. plays: %.2f" % avg_plays)
    play_rating = rating_sum / play_sum
    print("Weighted play rating: %.2f" % play_rating)


if __name__ == "__main__":
    # Ask for game to analyze.
    try:
        game_id, name = bgg_core.select_game()
        main(game_id, name)
    except ValueError:
        for game_id, name in bgg_core.get_games_by_rank_page(1):
            main(game_id, name)
