import csv
from bs4 import BeautifulSoup
import requests

base_url = "https://www.boardgamegeek.com/xmlapi2"


def get_data(base_type, params):
    """Download data from BGG API."""

    url = "/".join([base_url, base_type])
    response = requests.get(url, params)
    return response.text


def find_game(search):
    """Search for game matche."""

    query_dict = {"type": "boardgame", "query": search}
    response = get_data("search", query_dict)
    soup = BeautifulSoup(response, "xml")

    matches = {}

    for tag in soup.find_all("item"):
        id = tag["id"]
        name = tag.contents[1]["value"]
        matches[id] = name

    return matches


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

            ratings[row[0]] = row[1]

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
    print("Ratings: %s" % num_common_users)

    for ratings_dict in ratings_list:
        rating = sum(float(r) for u, r in ratings_dict.items()
                     if u in common_users)/num_common_users
        avg_ratings.append(rating)

    return avg_ratings


def main():
    """Compare game ratings between only users who have rated all games of interest."""

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

    all_ratings = []

    for game_id, name in games:

        ratings = {}
        filename = "%s.csv" % game_id

        try:
            ratings = read_ratings(filename)
        except:
            ratings = get_ratings(game_id)
            write_ratings(ratings, filename)

        all_ratings.append(ratings)

    avg_ratings = compare_ratings(all_ratings)

    for i in range(len(games)):
        print("Average rating for %s: %.2f" % (games[i][1], avg_ratings[i]))


if __name__ == "__main__":
    main()
