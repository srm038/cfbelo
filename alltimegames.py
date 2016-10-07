import requests as req
from bs4 import BeautifulSoup as bs
import re
from datetime import datetime

# TODO
# add doc_strings
# finish commenting
# separate everything into functions instead of autorun

r1 = re.compile('\n+')
r2 = re.compile(',([WLT]),')
r3 = re.compile('(\d\d\d\d),')
r4 = re.compile('\\\\')
r5 = re.compile(';')

def get_url(url):
    """Connect to the cfb website and return the raw page html"""

    response = req.get(url)
    html = response.content
    soup = bs(html, 'html.parser')
    
    return soup
    
def add_games(t, games_page):
    """
    """
    
    # sometimes the page doesnt respond right away
    # this just tries one more time to make sure it responds
    try:
        soup = get_url(games_page)
    except:
            try: soup = get_url(games_page)
            except: print(games_page)
    # this is the format for games on the cfbdatawarehouse site (FOR NOW)
    games = soup.find_all('td', attrs = {'bgcolor': '#E1D2D2'})
    # clean up the resulting code a bit so its one game per line
    games_text = r5.sub('',
        r3.sub('\g<1>,' + str(team_names[t]) + ',',
            r2.sub('\r\g<1>,',
                r1.sub('',
                    ','.join([g.text for g in games])))))
    # save what we've got so far
    with open(GAMES_FILE, 'a') as f:
        f.write(games_text)
        f.write('\n')

# grab names and urls of current D1 teams
# need to expand later to get all teams during the time they were D1?
# anyway, everything comes from this page and related lists
soup = get_url('http://cfbdatawarehouse.com/data/div_ia_team_index.php')
team_urls = [link.get('href')[:-9] for link in soup.find_all('a')
    if 'active' in link.get('href')]
team_names = [link.text for link in soup.find_all('a')
    if 'active' in link.get('href')]
for t, name in enumerate(team_names):
	if ';' in name: team_names[t] = name[:-1]

GAMES_FILE = r'allgames.txt'

# create or clear out existing data file
def clear_file():
    """
    """
    
    open(GAMES_FILE, 'w').close()

# loop through the D1 teams and grab all the game data

# for testing, use the following slices - the full data set takes a while
# and we want to avoid that if possible
# team_urls = team_urls[:5]
# years = years[:5]

def get_games():
    """
    """
    print('Getting games by team...')
    
    for t, team in enumerate(team_urls):
        soup = get_url('http://cfbdatawarehouse.com/data/' + team + 'index.php')
        
        years = [link.get('href') for link in soup.find_all('a')
            if 'yearly_results' in link.get('href')]
        
        for year in years:
            games_page ='http://cfbdatawarehouse.com/data/' + str(team) + str(year)
            add_games(t, games_page)
        
def clean_up(GAMES_FILE):
    """
    """
    
    print('Cleaning up data...')
    global games_dict
    games_list = []
    games_dict = []
    
    # read everything in the data file
    # a bit inefficient but makes sure the data gets saved somehow
    # in case things go wrong
    # they probably will
    
    with open(GAMES_FILE, 'r') as f:
        for line in f:
            games_list.append(line.split(','))
                
    for g in games_list:
        try:
            # need to be able to handle year-only games better
            # for now, they go at the beginning of the season-ish
            try: date = datetime.strptime(g[1], '%m-%d-%Y').strftime('%Y-%m-%d')
            except ValueError: date = g[1] + '-08-25'
            try: score2 = int(g[5])
            except ValueError: score2 = int(g[6])
            games_dict.append({
                'season': int(date[:4]) - (int(date[5:7]) < 7),
                'date': date,
                'team1': g[2],
                'score1': int(g[3]),
                'team2': g[4],
                'score2': score2
                })
        except IndexError:
            # this will occur during years the team didn't have a season
            # such as 1944
            pass
            
    games_dict.sort(key = lambda item:item['date'])
    
    print('# of games: ' + str(len(games_dict)))
    
    input('Press ENTER to continue...')
    
    global unique_games
    unique_games = set()
    
    # filter out duplicated games
    # set is best type of search here at O(1) * O(n)
    for g in games_dict:
        forward = ','.join([
                str(g['season']),
                g['date'],
                g['team1'],
                str(g['score1']),
                g['team2'],
                str(g['score2']),
                ])
        reverse = ','.join([
                str(g['season']),
                g['date'],
                g['team2'],
                str(g['score2']),
                g['team1'],
                str(g['score1']),
                ])
        if reverse not in unique_games: unique_games.add(forward)

    # turn it BACK into a list
    unique_games = sorted(unique_games)

    # see how many we were able to scrub out
    print('# of unique games: ' + str(len(unique_games)))

    # clean out the data file
    open(GAMES_FILE, 'w').close()

    # save the newly cleaned data back to the data file
    with open(GAMES_FILE, 'a') as f:
        for g in unique_games:
            f.write(g + '\n')

# get_games()
# clean_up(GAMES_FILE)