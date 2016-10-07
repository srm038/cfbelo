import alltimegames
from math import log
import matplotlib.pyplot as plt
import seaborn as sns

K = 17
INIT = 1500
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
    
seasons = dict(zip(
    TEAM_NAMES,
    [1869 for t in TEAM_NAMES]
    ))

def adjust(mov, elow = INIT, elol = INIT):
    """
    """
    
    adjust = K * log(abs(mov) + 1) * 2.2 / ((elow - elol) * 0.001 + 2.2)
    
    return adjust
    
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
        
def elo(game):
    """
    """
    
    team1 = game['team1']
    team2 = game['team2']
    elo1 = get_elo(team1)
    elo2 = get_elo(team2)
    
    # check for new season
    try:
        if seasons[team1] < game['season']:
            elo1 = elo1 + 0.25 * (INIT - elo1)
            seasons[team1] = game['season']
    except KeyError:
        pass
    try:
        if seasons[team2] < game['season']:
            elo2 = elo2 + 0.25 * (INIT - elo2)
            seasons[team2] = game['season']
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