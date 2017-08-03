import csv
import bgg_compare
from math import ceil


def main():
    """Compare top k-ranked games using condorcet method with an IRV tiebreaker as described in
    http://boardgamegeek.com/geeklist/161246/top-300-ranking-games-using-condorcet-irv-method/.
    """

    # Ask for number of games to compare.
    games = {}
    ranknum = int(input("Enter number of games to compare:"))
    pages = ceil(ranknum/100)
    games_list = []

    for page in range(1, pages):
        games_list += bgg_compare.get_games_by_rank_page(page)

    last_page_games = bgg_compare.get_games_by_rank_page(pages)
    remaining_games = ranknum % 100
    if remaining_games:
        games_list += last_page_games[:remaining_games]
    else:
        games_list += last_page_games

    games = dict(games_list)

    print("Comparing games:")

    all_ratings = []

    for game_id, name in games.items():

        print(name)

        ratings = {}
        filename = "%s.csv" % game_id

        try:
            ratings = bgg_compare.read_ratings(filename)
        except:
            ratings = bgg_compare.get_ratings(game_id)
            bgg_compare.write_ratings(ratings, filename)

        all_ratings.append(ratings)

    rankings = bgg_compare.condorcet_irv(all_ratings, list(games.keys()))

    print("Games ranked by Condorcet-IRV:")

    header = ["Rank", "ID", "Game", "Tiebreak"]
    print("\t".join(header))

    for i, (game_id, tiebreak) in enumerate(rankings, 1):
        print("\t".join([str(i), game_id, games[game_id], str(tiebreak)]))

    outfile = input("Enter filename to save results (leave empty to not save)")

    if outfile:
        with open(outfile, "w") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header)
            for i, (game_id, tiebreak) in enumerate(rankings, 1):
                writer.writerow([str(i), game_id, games[game_id], str(tiebreak)])


if __name__ == "__main__":
    main()
