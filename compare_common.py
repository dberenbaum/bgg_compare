import glob
import os
import bgg_compare


def main():
    """Compare ratings between users who have rated all games of interest."""

    # Ask for games to compare.
    games = []
    more_games = True

    while more_games:
        search = input("Enter board game to search (leave empty if finished):")

        if search:
            matches = bgg_compare.find_game(search)

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
        for f in glob.glob("[0-9]*.csv"):
            id = os.path.splitext(f)[0]
            ids.append(id)
        game_info = bgg_compare.get_game_info(ids)
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
            ratings = bgg_compare.read_ratings(filename)
        except:
            ratings = bgg_compare.get_ratings(game_id)
            bgg_compare.write_ratings(ratings, filename)

        all_ratings.append(ratings)

    avg_ratings = bgg_compare.compare_ratings(all_ratings)

    for i, game in enumerate(games):
        print("Average rating for %s: %.2f" % (game[1], avg_ratings[i]))


if __name__ == "__main__":
    main()
