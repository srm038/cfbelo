from operator import itemgetter
import os
import tempfile
import shutil
import teams

from math import log
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

K = 17
C = 2.2
P = 0.001
INIT = 1000
REG = 1 / 4
HERE = os.path.dirname(os.path.abspath(__file__))
GAMES_FILE = os.path.join(HERE, "allgames.csv")
TEAM_NAMES = []

for t in teams.top_division:
    TEAM_NAMES.append(t)

current_elo = dict(zip(TEAM_NAMES, [INIT for t in TEAM_NAMES]))

elo_history = dict(zip(TEAM_NAMES, [[] for t in TEAM_NAMES]))

elo_dates = dict(zip(TEAM_NAMES, [[] for t in TEAM_NAMES]))

game_dates = set()

seasons = dict(zip(TEAM_NAMES, [1869 for t in TEAM_NAMES]))

first_game = dict(
    zip(
        TEAM_NAMES,
        # indices
        [None for t in TEAM_NAMES],
    )
)


def adjust(mov, elow=INIT, elol=INIT):
    """ """

    adjust = K * log(abs(mov) + 1) * C / ((elow - elol) * P + C)

    return int(adjust)


def read_game(game):
    """ """

    if game == "\n":
        return
    g = game.split(",")

    try:
        return dict(
            zip(
                ["season", "date", "team1", "score1", "team2", "score2"],
                [int(g[0]), g[1], g[2], int(g[3]), g[4], int(g[5])],
            )
        )
    except ValueError:
        print(g)


def get_elo(team):
    """ """

    try:
        return current_elo[team]
    except KeyError:
        return INIT - 150


def set_elo(team, elo):
    """ """

    if team in current_elo:
        current_elo.update({team: elo})
    else:
        pass


def top_div(team, year):
    """
    Returns True if a team is currently in the top division at the time
    """

    try:
        return int(year) in teams.top_division[team]
    except KeyError:
        return False


def elo(game):
    """ """

    team1 = game["team1"]
    team2 = game["team2"]
    elo1 = get_elo(team1)
    elo2 = get_elo(team2)
    season = game["season"]

    # check for division membership

    if not top_div(team1, season):
        print(f"{team1} was not in the top division in {season} (vs {team2})")
        return
    if not top_div(team2, season):
        print(f"{team2} was not in the top division in {season} (vs {team1})")
        return

    # add first game

    game_dates.add(game["date"])
    if not first_game[team1]:
        first_game.update({team1: game["date"]})
    if not first_game[team2]:
        first_game.update({team2: game["date"]})

    # check for new season
    try:
        since = season - seasons[team1]
        while since > 0:
            elo1 += int(REG * (INIT - elo1))
            since -= 1
        else:
            seasons[team1] = season
    except KeyError:
        pass
    try:
        since = season - seasons[team2]
        while since > 0:
            elo2 += int(REG * (INIT - elo2))
            since -= 1
        else:
            seasons[team2] = season
    except KeyError:
        pass

    game.update({"previous1": elo1})
    game.update({"previous2": elo2})

    if elo1 > elo2 and game["score1"] > game["score2"]:
        game.update({"accuracy": 1})
    elif elo1 < elo2 and game["score1"] < game["score2"]:
        game.update({"accuracy": 1})
    elif game["score1"] == game["score2"]:
        game.update({"accuracy": 0.5})
    else:
        game.update({"accuracy": 0})

    if team1 not in TEAM_NAMES or team2 not in TEAM_NAMES:
        game.update({"elo1": elo1})
        game.update({"elo2": elo2})
        if team1 in TEAM_NAMES:
            elo_history[team1].append(elo1)
            elo_dates[team1].append(game["date"])
        if team2 in TEAM_NAMES:
            elo_history[team2].append(elo2)
            elo_dates[team2].append(game["date"])
        return

    mov = game["score1"] - game["score2"]

    if mov > 0:
        adj = adjust(abs(mov), elo1, elo2)
        elo1 += adj
        elo2 -= adj
        game.update({"change1": adj})
        game.update({"change2": -adj})
    elif mov < 0:
        adj = adjust(abs(mov), elo2, elo1)
        elo1 -= adj
        elo2 += adj
        game.update({"change1": -adj})
        game.update({"change2": adj})
    else:
        game.update({"change1": 0})
        game.update({"change2": 0})

    set_elo(team1, elo1)
    set_elo(team2, elo2)
    game.update({"elo1": elo1})
    game.update({"elo2": elo2})
    game.update({"eloCombined": elo1 + elo2})
    elo_history[team1].append(elo1)
    elo_history[team2].append(elo2)
    elo_dates[team1].append(game["date"])
    elo_dates[team2].append(game["date"])
    return game


def accuracy():

    acc = sum([g.get("accuracy", 0) for g in games])
    return acc / len(games)


def print_elo(game, file=None):
    """ """

    if not top_div(game["team1"], game["season"]) or not top_div(
        game["team2"], game["season"]
    ):
        return

    out = (
        ",".join(
            [
                str(game["season"]),
                game["date"],
                game["team1"],
                str(game["score1"]),
                game["team2"],
                str(game["score2"]),
                str(game["elo1"]),
                str(game["elo2"]),
                str(game["change1"]),
                str(game["change2"]),
            ]
        )
        + "\n"
    )
    if file:
        file.write(out)
    else:
        with open(GAMES_FILE, "a") as f:
            f.write(out)


global games
averageelo = []
games = []


def do_all_elo():
    """

    :return:
    """

    global games
    games.clear()

    with open(GAMES_FILE, "r") as f:
        for line in f:
            games.append(read_game(line))
    print(len(games))

    fd, tmp_path = tempfile.mkstemp(dir=os.path.dirname(GAMES_FILE) or ".")
    with os.fdopen(fd, "w") as tmp:
        for game in games:
            if game:
                elo(game)
                print_elo(game, file=tmp)
    shutil.move(tmp_path, GAMES_FILE)

    global averageelo
    firstseason = games[0]["season"]
    lastseason = games[-1]["season"]
    for y in range(firstseason, lastseason + 1):
        e1 = []
        e2 = []
        for g in games:
            if g["season"] == y:
                try:
                    e1.append(g["elo1"])
                except KeyError:
                    print(g)
                try:
                    e2.append(g["elo2"])
                except KeyError:
                    print(g)
        e = e1 + e2
        averageelo.append(avg(e))
    averageelo = [a for a in averageelo if a != 0]


def sinuosity(t, start=None, end=None):

    if not start:
        start = games[0]["season"]
    if not end:
        end = games[-1]["season"]
    total = []
    try:
        a = season_end(t, start)
    except:
        a = 1000
    b = season_end(t, end)
    for g in games:
        if g["season"] in range(start, end + 1):
            if g["team1"] == t:
                total.append(abs(g["change1"]))
            if g["team2"] == t:
                total.append(abs(g["change2"]))
    return sum(total) / abs(b - a)


def top_games(n):

    games_top = sorted(games, key=itemgetter("eloCombined"), reverse=True)
    for i in range(0, n):
        print(
            "{:} {: >25} ({: >4}) vs. {: <25} ({: <4})".format(
                games_top[i]["date"],
                games_top[i]["team1"],
                games_top[i]["elo1"],
                games_top[i]["team2"],
                games_top[i]["elo2"],
            )
        )


def season_end(t, y):

    temp = [
        g for g in games if (g["team1"] == t or g["team2"] == t) and g["season"] == y
    ]
    if temp[-1]["team1"] == t:
        return temp[-1]["elo1"]
    else:
        return temp[-1]["elo2"]


def top_wins(n):

    for g in games:
        g.update({"change": abs(g["change1"])})
    games_top = sorted(games, key=itemgetter("change"), reverse=True)

    games_top = sorted(games, key=itemgetter("change"), reverse=True)

    for i in range(0, n):
        if games_top[i]["score1"] > games_top[i]["score2"]:
            print(
                "{:} {: >25} ({: >4}) vs. {: <25} ({: <4}) : {:+d}".format(
                    games_top[i]["date"],
                    games_top[i]["team1"],
                    games_top[i]["elo1"],
                    games_top[i]["team2"],
                    games_top[i]["elo2"],
                    games_top[i]["change1"],
                )
            )
        else:
            print(
                "{:} {: >25} ({: >4}) vs. {: <25} ({: <4}) : {:+d}".format(
                    games_top[i]["date"],
                    games_top[i]["team2"],
                    games_top[i]["elo2"],
                    games_top[i]["team1"],
                    games_top[i]["elo1"],
                    games_top[i]["change2"],
                )
            )


def w(team, game):

    dr = (game["elo1"] - game["elo2"]) if team == game["team1"] else (game["elo2"] - game["elo1"])
    w = 1 / (10 ** (-dr / 400) + 1)
    return w


def w2(t1: str, t2: str) -> float:
    g = {
        "team1": t1,
        "elo1": elo_history[t1][-1],
        "team2": t2,
        "elo2": elo_history[t2][-1],
    }
    return w(t1, g)


def waa(team, season):
    """Assume you are an average team (1000) for every game. How many wins do you have at the end of the season?"""

    waa = 0
    waap = 0
    aw = 0
    for g in games:
        if team not in [g["team1"], g["team2"]]:
            continue
        if season != g["season"]:
            continue
        if team == g["team1"]:
            if g["score1"] > g["score2"]:
                aw += 1
            if 1000 > g["elo2"]:
                waa += 1
        else:
            if g["score2"] > g["score1"]:
                aw += 1
            if 1000 > g["elo1"]:
                waa += 1
        waap += w(team, g)
    return aw - waa, aw - waap, aw


def team_games(t, start=None, end=None):

    if not start:
        start = games[0]["season"]
    if not end:
        end = games[-1]["season"]
    for g in games:
        try:
            if g["season"] in range(start, end + 1):
                if g["team1"] == t:
                    print(
                        "{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}".format(
                            g["date"],
                            g["team2"],
                            g["score1"],
                            g["score2"],
                            g["elo1"],
                            g["elo2"],
                            g["previous1"],
                            g["previous2"],
                            g["change1"],
                        )
                    )
                if g["team2"] == t:
                    print(
                        "{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}\t{:}".format(
                            g["date"],
                            g["team1"],
                            g["score2"],
                            g["score1"],
                            g["elo2"],
                            g["elo1"],
                            g["previous2"],
                            g["previous1"],
                            g["change2"],
                        )
                    )
        except KeyError:
            print(g)
            pass


def team_performance(t):

    ww = []
    wl = []
    lw = []
    ll = []

    for g in games:
        if g["team1"] == t:
            diff = g["previous1"] - g["previous2"]
            outcome = g["score1"] - g["score2"]
        elif g["team2"] == t:
            diff = g["previous2"] - g["previous1"]
            outcome = g["score2"] - g["score1"]
        else:
            continue
        if diff >= 0 and outcome >= 0:
            ww.append(1)
        if diff >= 0 and outcome < 0:
            wl.append(1)
        if diff < 0 and outcome >= 0:
            lw.append(1)
        if diff < 0 and outcome < 0:
            ll.append(1)
    n = len([g for g in games if g["team1"] == t or g["team2"] == t])
    return "{:},{:.2f},{:.2f},{:.2f},{:.2f}".format(
        t,
        len(ww) / n if n != 0 else 0,
        len(wl) / n if n != 0 else 0,
        len(lw) / n if n != 0 else 0,
        len(ll) / n if n != 0 else 0,
    )


def show_all():
    csvdata = os.path.join(HERE, "Elo.csv")

    with open(csvdata, "w") as f:
        i = 1
        f.write("Rank\tTeam\tElo\tmin Elo\tmax Elo\tPotential\n")
        for t in sorted(current_elo, key=lambda x: current_elo[x], reverse=True):
            if top_div(t, 2025):
                now_elo = current_elo[t]
                min_elo = min(elo_history[t]) if elo_history[t] else 0
                max_elo = max(elo_history[t]) if elo_history[t] else 1000
                try:
                    potential = 100 * (now_elo - min_elo) / (max_elo - min_elo)
                except ZeroDivisionError:
                    potential = 100
                print(
                    "{:}\t{:}\t{:}\t{:}\t{:.2f}".format(
                        t, now_elo, min_elo, max_elo, potential
                    )
                )
                f.write(
                    "{:}\t{:}\t{:}\t{:}\t{:}\t{:.2f}\n".format(
                        i, t, now_elo, min_elo, max_elo, potential
                    )
                )
                i += 1


def plot_history(team, col=[], plot_all=True, start=0, end=None):
    """
    TODO: extend this function to handle arbitrary # of teams
    """

    while len(col) < len(team):
        col.append((0, 0, 255))

    for t in team:
        if t not in elo_history:
            raise TeamNotFound

    dates = sorted(game_dates)

    for d, date in enumerate(dates):
        if season(date) == start:
            start = d
            break

    if not end:
        end = len(dates) - 1
    else:
        for d, date in enumerate(dates):
            if season(date) + 1 == end:
                start = d - 1
                break

    def format_date(x, pos=None):
        x = max(0, min(int(x + 0.5), len(dates) - 1))
        return dates[x][:4]

    mpl.rcParams["font.family"] = "Ubuntu Mono"

    fig = plt.figure(
        facecolor="white",
        figsize=(6, 5),
        frameon=False,
        tight_layout=True,
    )
    ax = fig.add_subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # gridlines
    ax.axhline(
        1000,
        ls="-",
        color=((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
        lw=0.5,
    )
    ax.axhline(
        2000,
        ls="-",
        color=((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
        lw=0.5,
    )
    ax.axhline(
        0,
        ls="-",
        color=((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
        lw=0.5,
    )

    if plot_all:
        for t in elo_history:
            ax.scatter(
                [dates.index(d) for d in elo_dates[t]],
                elo_history[t],
                color=((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
                alpha=1 / 32 * (1 - bool(start)) + 1 / 8 * bool(start),
                s=5,
            )
    for t, c in zip(team, col):
        ax.scatter(
            [dates.index(d) for d in elo_dates[t]],
            elo_history[t],
            facecolor=(c[0] / 255, c[1] / 255, c[2] / 255),
            # edgecolor = ((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
            edgecolor=(1, 1, 1),
            s=7 * (1 - bool(start)) + 15 * bool(start),
        )

    plt.xlim(start, end)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    fig.autofmt_xdate()
    for tick in ax.get_xticklabels():
        tick.set_rotation(0)

    if len(team) == 1:
        plt.title(
            team[0],
            loc="left",
            family="Ubuntu Mono",
            weight="bold",
            # va = 'bottom',
            y=0.95,
            x=0.05,
            size=14,
            bbox=dict(facecolor="white", alpha=0.75, edgecolor="none"),
            alpha=0.75,
        )

    plt.show()


def avg(L):
    if len(L) == 0:
        return 0
    else:
        return sum(L) / len(L)


def plot_average():
    plt.scatter(
        list(range(games[0]["season"], games[0]["season"] + len(averageelo))),
        averageelo,
    )


class TeamNotFound(Exception):
    """Raise when a team is not defined or doesn't exist"""

    pass


def season(date):
    """

    :param date:
    :return:
    """

    season = int(date[:4]) - (int(date[5:7]) < 7)

    return season


def team_candles(t, start=None, end=None):

    if not start:
        start = games[0]["season"]
    if not end:
        end = games[-1]["season"]
    candles = list()
    for s in range(start, end + 1):
        candle = list()
        for g in games:
            if g["season"] == s and t in [g["team1"], g["team2"]]:
                candle.append(g)
        candle = [
            c["elo1"] if c["team1"] == t else c["elo2"]
            for c in candle
            if "elo1" in c and "elo2" in c
        ]
        if not candle:
            continue
        candles.append(
            {
                "open": candle[0],
                "close": candle[-1],
                "low": min(candle),
                "high": max(candle),
            }
        )
        print(f"{s}\t{candle[0]}\t{max(candle)}\t{min(candle)}\t{candle[-1]}")
    return candles


if __name__ == "__main__":
    do_all_elo()
    show_all()
