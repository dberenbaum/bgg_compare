import csv
import glob
import os
import bgg_compare


def main():
    """Compare games using condorcet method with an IRV tiebreaker as described in
    http://boardgamegeek.com/geeklist/161246/top-300-ranking-games-using-condorcet-irv-method/.
    """

    # Ask for games to compare.
    games = {}
    more_games = True

    while more_games:
        search = input("Enter board game to search (leave empty if finished):")

        if search:
            matches = bgg_compare.find_game(search)

            print("Games found:")
            for game_id, name in matches.items():
                print(game_id + "\t" + name)
            id = input("Enter the number before the intended game:")
            games[id] = matches[id]

        else:
            more_games = False

    # If no games entered, compare all downloaded ratings.
    if not games:
        ids = []
        for f in glob.glob("[0-9]*.csv"):
            id = os.path.splitext(f)[0]
            ids.append(id)
        game_info = bgg_compare.get_game_info(ids)
        for i, info in enumerate(game_info):
            name = info.find("name", attrs={"type": "primary"})["value"]
            games[ids[i]] = name

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
