import csv
import glob
import os
import numpy as np
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


def get_ratings(id):
    """Get ratings for game with given id."""

    query_dict = {"id": id, "ratingcomments": 1, "pagesize": 100}
    page = 1
    more_pages = True
    ratings = {}

    while more_pages:

        more_pages = False

        query_dict["page"] = page
        response = get_data("thing", query_dict)
        soup = BeautifulSoup(response, "xml")

        for tag in soup.find_all("comment"):
            ratings[tag["username"]] = tag["rating"]
            more_pages = True

        print("Parsed page %s for game id %s" % (page, id))

        page += 1

    return ratings


def write_ratings(ratings, filename):
    """Save ratings dict to csv to reduce repetitive scraping."""

    with open(filename, "w") as csvfile:

        writer = csv.writer(csvfile)

        writer.writerows(list(ratings.items()))


def read_ratings(filename):
    """Read ratings from csv into dict."""

    ratings = {}

    with open(filename) as csvfile:

        reader = csv.reader(csvfile)

        for row in reader:

            ratings[row[0]] = float(row[1])

    return ratings


def compare_ratings(ratings_list):
    """
    Compare ratings among common users.
    Takes a list of dicts with user-rating as key-value pairs.
    Returns a list of average ratings among common users between all lists.
    """

    avg_ratings = []
    all_users = [list(r.keys()) for r in ratings_list]

    common_users = set.intersection(*map(set, all_users))
    num_common_users = len(common_users)
    if not num_common_users:
        raise ValueError("Zero common users between games.")
    print("Ratings: %s" % num_common_users)

    for ratings_dict in ratings_list:
        rating = sum(float(r) for u, r in ratings_dict.items()
                     if u in common_users)/num_common_users
        avg_ratings.append(rating)

    return avg_ratings


def condorcet_irv(ratings_list, ids):
    """
    Rank games by condorcet method.
    Takes a list of dicts with user-rating as key-value pairs and a list of game ids.
    Returns a list of average ratings among common users between all lists.
    """

    num_games = len(ratings_list)
    users = list({user for u in ratings_list for user in list(u.keys())})
    ranks = []

    # Get info for IRV tiebreaker.
    irv = np.zeros((num_games,), dtype=[("top_rating", "<i4"), ("votes", "<i4"),
                                          ("year", "<i4"), ("id", "<i4")])
    game_info = get_game_info(ids)
    for i, info in enumerate(game_info):
        irv[i]["year"] = info.find("yearpublished")["value"]
        irv[i]["id"] = int(ids[i])

    # Create matrix of all games/users.
    user_game_mat = np.zeros((num_games, len(users)))
    for i, ratings in enumerate(ratings_list):
        irv[i]["votes"] = len(ratings)
        for j, user in enumerate(users):
            user_game_mat[i,j] = ratings.get(user, np.nan)

    # Generate matrix showing how many times game was favored in pairwise comparison.
    cond_mat = np.apply_along_axis(lambda x: np.apply_along_axis(np.sum, 1, x > user_game_mat),
                        1, user_game_mat)

    # For IRV tiebreaker, how many times game was a user's top ranked game.
    top_ratings = np.max(user_game_mat, 0)
    irv[:]["top_rating"] = np.apply_along_axis(lambda x: np.sum(top_ratings == x),
                                               1, user_game_mat)

    # Subtract columns from rows to show pairwise difference between games.
    diff_mat = cond_mat - cond_mat.T
    np.fill_diagonal(diff_mat, 1)

    # Get tiebreak order.
    max_year = np.max(irv[:]["year"])
    irv[:]["year"] = max_year - irv[:]["year"]
    max_id = np.max(irv[:]["id"])
    irv[:]["id"] = max_id - irv[:]["id"]

    # Rank by condorcet-IRV method.
    while len(irv):
        temp_mat = diff_mat.copy()
        temp_irv = irv.copy()
        # Find condorcet winner.
        winners = []
        while not len(winners):
            # Winning rows are all positive.
            winners = np.where(np.all(temp_mat > 0, axis=1))[0]
            assert len(winners) <= 1, "multiple winners found"
            if len(winners):
                temp_id = temp_irv[winners[0]]["id"]
                winning_ix = np.where(irv[:]["id"] == temp_id)[0][0]
                diff_mat = np.delete(diff_mat, winning_ix, axis=0)
                diff_mat = np.delete(diff_mat, winning_ix, axis=1)
                irv = np.delete(irv, winning_ix)
                winning_id = -(temp_id - max_id)
                ranks.append(str(winning_id))
            else:
                # Remove plurality loser.
                tiebreak = np.argsort(temp_irv, order=("top_rating", "votes", "year", "id"))
                plurality_loser = tiebreak[0]
                temp_mat = np.delete(temp_mat, plurality_loser, axis=0)
                temp_mat = np.delete(temp_mat, plurality_loser, axis=1)
                temp_irv = np.delete(temp_irv, plurality_loser)

    return ranks


def main():
    """Compare ratings between users who have rated all games of interest."""

    # Ask for games to compare.
    games = []
    more_games = True

    while more_games:
        search = input("Enter board game to search (leave empty if finished):")

        if search:
            matches = find_game(search)

            print("Games found:")
            for game_id, name in matches.items():
                print(game_id + "\t" + name)
            id = input("Enter the number before the intended game:")
            games.append((id, matches[id]))

        else:
            more_games = False

    # If no games entered, compare all downloaded ratings.
    if not games:
        ids = []
        for f in glob.glob("*.csv"):
            id = os.path.splitext(f)[0]
            ids.append(id)
        game_info = get_game_info(ids)
        for i, info in enumerate(game_info):
            name = info.find("name", attrs={"type": "primary"})["value"]
            games.append((ids[i], name))

    print("Comparing games:")

    all_ratings = []

    for game_id, name in games:

        print(name)

        ratings = {}
        filename = "%s.csv" % game_id

        try:
            ratings = read_ratings(filename)
        except:
            ratings = get_ratings(game_id)
            write_ratings(ratings, filename)

        all_ratings.append(ratings)

    avg_ratings = compare_ratings(all_ratings)

    for i, game in enumerate(games):
        print("Average rating for %s: %.2f" % (game[1], avg_ratings[i]))


if __name__ == "__main__":
    main()
