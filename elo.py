import alltimegames
import teams

from math import log
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
from datetime import datetime

K = 17
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
    
    adjust = K * log(abs(mov) + 1) * 2.2 / ((elow - elol) * 0.001 + 2.2)
    
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
    
    try: return int(year) in teams.top_division[team]
    except KeyError: return False
        
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
        if seasons[team1] < season:
            elo1 = elo1 + int(0.25 * (INIT - elo1))
            seasons[team1] = season
    except KeyError:
        pass
    try:
        if seasons[team2] < season:
            elo2 = elo2 + int(0.25 * (INIT - elo2))
            seasons[team2] = season
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
                
def do_all_elo():

    temp_games = []

    with open(GAMES_FILE, 'r') as f:
        for line in f:
            temp_games.append(read_game(line))
    
    alltimegames.clear_file()
    
    for game in temp_games:
        elo(game)
        print_elo(game)
        
    del temp_games
    
def show_all():

    for t in current_elo:
        if top_div(t, 2016):
            print('{:}\t{:}'.format(t, current_elo[t]))
    
def plot_history(team, col):
    """
    TODO: extend this function to handle arbitray # of teams
    """
    
    while len(col) < len(team):
        col.append((0, 0, 255))
    
    for t in team:
        if t not in elo_history:
            raise TeamNotFound
    
    dates = sorted(game_dates)
    
    def format_date(x, pos = None):
        x = max(0, min(int(x + 0.5), len(dates) - 1))
        return dates[x][:4]
    
    sns.set_style('whitegrid')
    fig = plt.figure(
        facecolor = 'white',
        figsize = (8, 6),
        frameon = False,
        tight_layout = True)
    ax = fig.add_subplot(111)
    
    for t in elo_history:
        ax.scatter(
            [dates.index(d) for d in elo_dates[t]],
            elo_history[t],
            color = ((17 + 100)/255, (28 + 100)/255, (36 + 100)/255),
            alpha = 1/32,
            s = 5)
    for t, c in zip(team, col):
        ax.scatter(
            [dates.index(d) for d in elo_dates[t]],
            elo_history[t],
            facecolor = (c[0] / 255, c[1] / 255, c[2] / 255),
            edgecolor = 'k',
            s = 7)
    
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    fig.autofmt_xdate()
    plt.show()
    
class TeamNotFound(Exception):
    """Raise when a team is not defined or doesn't exist"""
    pass