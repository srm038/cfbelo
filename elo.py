import alltimegames
from math import log

K = 14
INIT = 1500

def adjust(mov, elow = INIT, elol = INIT):
    """
    """
    
    adjust = K * log(abs(mov) + 1) * 2.2 / (( elow - elol) * 0.001 + 2.2)
    
    return adjust
    
def read_game(game):
    """
    """
    
    g = game.split(',')
    
    return dict(zip(
        ['date', 'team1', 'score1', 'team2', 'score2'],
        [g[0], g[1], int(g[2]), g[3], int(g[4])]
        ))