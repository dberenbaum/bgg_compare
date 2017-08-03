import bgg_compare
import requests
from bs4 import BeautifulSoup


def main():
    """Download top-ranked game ratings if not already saved."""

    page = input("Enter the page of rankings to get:")

    games = bgg_compare.get_games_by_rank_page(page)

    for game_id, name in games:
        filename = "%s.csv" % game_id
        print(name)
        try:
            ratings = bgg_compare.read_ratings(filename)
        except:
            ratings = bgg_compare.get_ratings(game_id)
            bgg_compare.write_ratings(ratings, filename)


if __name__ == "__main__":
    main()
