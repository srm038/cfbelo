# CFB Elo

## Goal

The purpose of this project is to build a ground-up Elo rating system for college football teams. This will utilize games from all times in American football history.

## Challenges

### Data

While data for all games from all time does exist, it's fairly fragmented. As usual, the first and biggest challenge to any data analysis project is getting the data into a workable format. I'm scraping from the [CFB Data Warehouse](http://cfbdatawarehouse.com/index.php) for now.

### Design Options

I'll be basing a lot of the actual rating system on [Five Thirty-Eight's NFL Elo Ratings](http://fivethirtyeight.com/datalab/nfl-elo-ratings-are-back/). However, the professional nature of this league (as well as the NBA Ratings, also by Five Thirty-Eight) means that it's largely a closed system, and it's relatively simple to deal with expansion teams. There are also always less than 50 teams at any one time.  

College is much more complicated, if even by the additional number of teams. CFB Data Warehouse provides mostly complete data on teams from FBS, FCS, Div II, Div III, NAIA, and even NCCAA. Parameter choice aside, I have to come up with some rule to choose which teams to include. We have a few options:

* Include all teams for which data is available. With this, we run into the problem of choosing initial Elo values for multiple levels of teams.

* Include all teams that are currently FBS, as well as any teams during which time they were in the top division (e.g., Princeton pre-1930s). This has the disadvantage of "locking" the ratings to this particular year (2016). This can theoretically be solved by including every team for which there is data up until classification, so that there's a value in the system for that team should they rejoin FBS later. Expansion is not as simple as in the professional leagues, since classification is much more complicated. Many teams dropped down to Division II in the 70s, only to make their way back up to the FBS ranks. It's not inconceivable that could happen again, and we want to be sure that our ranking is more or less immutable. For example, Bowling Green's 1920 game against Defiance College should have the same value whether or not Defiance ever makes it up out of Div III (admittedly unlikely). We could take data from all teams until 1937 (or appropriate re-classification) and let them maintain their (mean-regressed) Elo until the event they rejoined FBS.

* Include only current FBS teams. Again, we run into the problem of how to handle expansion teams.

Once we've chosen our set of teams, we are always going to be faced with the problem of how to handle games outside that set. This will always be a problem because early in football's history, teams would regularly play high schools, YMCAs, and other athletic groups. We could probably safely ignore these games (though I guarantee you those schools still count the wins!).

### History

The NCAA as we know it wasn't founded until 1906 as the IAAUS, almost 40 years after the first football game.

In 1937, the NCAA introduced classification, but many teams weren't officially categorized into University or College Division until much later.

In 1973, these two divisions further divided into Divisions I, II, and III.

In 1978, Division I split yet again into I-A and I-AA, which would later be renamed FBS and FCS, respectively.

## Python Packages Used

* requests
* beautifulsoup
* re
* datetime
