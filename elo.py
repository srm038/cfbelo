import alltimegames
import teams

from math import log
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from datetime import datetime

K = 17
C = 2.2
P = 0.001
INIT = 1000
GAMES_FILE = alltimegames.GAMES_FILE
TEAM_NAMES = alltimegames.team_names

current_elo = dict(zip(
    TEAM_NAMES,
    [INIT for t in TEAM_NAMES]
))

elo_history = dict(zip(
    TEAM_NAMES,
    [[] for t in TEAM_NAMES]
))

elo_dates = dict(zip(
    TEAM_NAMES,
    [[] for t in TEAM_NAMES]
))

game_dates = set()

seasons = dict(zip(
    TEAM_NAMES,
    [1869 for t in TEAM_NAMES]
))

first_game = dict(zip(
    TEAM_NAMES,
    # indices
    [None for t in TEAM_NAMES]
))

def adjust(mov, elow = INIT, elol = INIT):
    """
    """

    adjust = K * log(abs(mov) + 1) * C / ((elow - elol) * P + C)

    return int(adjust)


def read_game(game):
    """
    """

    g = game.split(',')

    return dict(zip(
        ['season', 'date', 'team1', 'score1', 'team2', 'score2'],
        [int(g[0]), g[1], g[2], int(g[3]), g[4], int(g[5])]
    ))


def get_elo(team):
    """
    """

    try:
        return current_elo[team]
    except KeyError:
        return INIT - 150


def set_elo(team, elo):
    """
    """

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
    """
    """

    team1 = game['team1']
    team2 = game['team2']
    elo1 = get_elo(team1)
    elo2 = get_elo(team2)
    season = game['season']

    # check for division membership

    if not top_div(team1, season) or not top_div(team2, season):
        return

    # add first game

    game_dates.add(game['date'])
    if not first_game[team1]: first_game.update({team1: game['date']})
    if not first_game[team2]: first_game.update({team2: game['date']})

    # check for new season
    try:
        since = season - seasons[team1]
        while since > 0:
            elo1 += int(0.25 * (INIT - elo1))
            since -= 1
        else:
            seasons[team1] = season
        # if seasons[team1] < season:
        #     elo1 += int(0.25 * (INIT - elo1))
        #     seasons[team1] = season
    except KeyError:
        pass
    try:
        since = season - seasons[team2]
        while since > 0:
            elo2 += int(0.25 * (INIT - elo2))
            since -= 1
        else:
            seasons[team2] = season
        # if seasons[team2] < season:
        #     elo2 += int(0.25 * (INIT - elo2))
        #     seasons[team2] = season
    except KeyError:
        pass

    if team1 not in TEAM_NAMES or team2 not in TEAM_NAMES:
        game.update({'elo1': elo1})
        game.update({'elo2': elo2})
        if team1 in TEAM_NAMES:
            elo_history[team1].append(elo1)
            elo_dates[team1].append(game['date'])
        if team2 in TEAM_NAMES:
            elo_history[team2].append(elo2)
            elo_dates[team2].append(game['date'])
        return

    mov = game['score1'] - game['score2']

    if mov > 0:
        adj = adjust(abs(mov), elo1, elo2)
        elo1 += adj
        elo2 -= adj
    elif mov < 0:
        adj = adjust(abs(mov), elo2, elo1)
        elo1 -= adj
        elo2 += adj

    set_elo(team1, elo1)
    set_elo(team2, elo2)
    game.update({'elo1': elo1})
    game.update({'elo2': elo2})
    elo_history[team1].append(elo1)
    elo_history[team2].append(elo2)
    elo_dates[team1].append(game['date'])
    elo_dates[team2].append(game['date'])


def print_elo(game):
    """
    """

    if (not top_div(game['team1'], game['season']) or
            not top_div(game['team2'], game['season'])):
        return

    with open(GAMES_FILE, 'a') as f:
        f.write(','.join([
            str(game['season']),
            game['date'],
            game['team1'],
            str(game['score1']),
            game['team2'],
            str(game['score2']),
            str(game['elo1']),
            str(game['elo2']),
        ]) + '\n')

averageelo = []

def do_all_elo():

    global games
    games = []

    with open(GAMES_FILE, 'r') as f:
        for line in f:
            games.append(read_game(line))

    alltimegames.clear_file()

    for game in games:
        elo(game)
        print_elo(game)

    global averageelo
    # averageelo = []
    firstseason = games[0]['season']
    lastseason = games[-1]['season']
    for y in range(firstseason, lastseason + 1):
        e1 = [game['elo1'] for game in games if game['season'] == y]
        e2 = [game['elo2'] for game in games if game['season'] == y]
        e = e1 + e2
        averageelo.append(avg(e))
    averageelo = [a for a in averageelo if a != 0]


def show_all():
    for t in current_elo:
        if top_div(t, 2016):
            now_elo = current_elo[t]
            min_elo = min(elo_history[t])
            max_elo = max(elo_history[t])
            potential = 100 * (now_elo - min_elo) / (max_elo - min_elo)
            print('{:}\t{:}\t{:}\t{:}\t{:.2f}'.format(t, now_elo, min_elo, max_elo, potential))


def plot_history(team, col, plot_all = True, start = 0, end = None):
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

    def format_date(x, pos = None):
        x = max(0, min(int(x + 0.5), len(dates) - 1))
        return dates[x][:4]

    mpl.rcParams['font.family'] = 'Ubuntu Mono'

    fig = plt.figure(
        facecolor = 'white',
        figsize = (5, 4),
        frameon = False,
        tight_layout = True,
    )
    ax = fig.add_subplot(111, axisbg = 'white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # gridlines
    ax.axhline(
        1000,
        ls = '-',
        color = ((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
        lw = 0.5,
    )
    ax.axhline(
        2000,
        ls = '-',
        color = ((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
        lw = 0.5,
    )
    ax.axhline(
        0,
        ls = '-',
        color = ((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
        lw = 0.5,
    )

    if plot_all:
        for t in elo_history:
            ax.scatter(
                [dates.index(d) for d in elo_dates[t]],
                elo_history[t],
                color = ((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
                alpha = 1 / 32 * (1 - bool(start)) + 1 / 4 * bool(start),
                s = 5)
    for t, c in zip(team, col):
        ax.scatter(
            [dates.index(d) for d in elo_dates[t]],
            elo_history[t],
            facecolor = (c[0] / 255, c[1] / 255, c[2] / 255),
            edgecolor = ((17 + 100) / 255, (28 + 100) / 255, (36 + 100) / 255),
            s = 7 * (1 - bool(start)) + 10 * bool(start))

    plt.xlim(start, end)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    fig.autofmt_xdate()
    for tick in ax.get_xticklabels():
        tick.set_rotation(0)

    if len(team) == 1:
        plt.title(team[0],
            loc = 'left',
            family = 'Ubuntu Mono',
            weight = 'bold',
            # va = 'bottom',
            y = 0.95,
            x = 0.05,
            size = 14,
            bbox = dict(facecolor = 'white', alpha = 0.75, edgecolor = 'none'),
            alpha = 0.75)

    plt.show()

def avg(L):

    if len(L) == 0:
        return 0
    else:
        return sum(L) / len(L)

def plot_average():

    plt.scatter(
        list(range(games[0]['season'], games[0]['season'] + len(averageelo))),
        averageelo
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