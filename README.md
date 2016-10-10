# CFB Elo

## Goal

The purpose of this project is to build a ground-up Elo rating system for college football teams. This will utilize games from all times in American football history.

## Challenges

### Data

While data for all games from all time does exist, it's fairly fragmented. As usual, the first and biggest challenge to any data analysis project is getting the data into a workable format. I'm scraping from the [CFB Data Warehouse](http://cfbdatawarehouse.com/index.php) for now.

### Design Options

I'll be basing a lot of the actual rating system on [Five Thirty-Eight's NFL Elo Ratings](http://fivethirtyeight.com/datalab/nfl-elo-ratings-are-back/). However, the professional nature of this league (as well as the NBA Ratings, also by Five Thirty-Eight) means that it's largely a closed system, and it's relatively simple to deal with expansion teams. There are also always less than 50 teams at any one time.  

College is much more complicated, if even by the additional number of teams. CFB Data Warehouse provides mostly complete data on teams from FBS, FCS, Div II, Div III, NAIA, and even NCCAA. Parameter choice aside, I have to come up with some rule to choose which teams to include.

Eventually, I decided to consider teams that played in the top division during the following eras:

* Pre-1937. Many teams dropped to lower divisions at this time, if they hadn't ceased entirely already.
* University Division
* Division I
* Division I-A (or FBS)

If a team dropped out but got back in, their Elo was preserved. This has the added design benefit of preserving a value for teams that have yet to move into the FBS but have played previously. There are increasingly fewer teams that this applies to, but we can handle them nonetheless.

Originally, I had intended to punish teams for losing to out-of-division opponents, but it's much simpler to disregard these games altogether, much like FIFA disregards friendly matches.

So far, I have data for games from all of Divisions I and II, and most of III.

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
* matplotlib
* seaborn
