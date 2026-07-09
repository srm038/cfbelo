# CFB Elo

Ground-up Elo rating system for college football, covering games from 1869 through the 2026 season.

## Data

All games are in `allgames.csv` — a CSV with columns:
`season,date,team1,score1,team2,score2,elo1,elo2,change1,change2`

~76,000 games spanning 1869–2026, covering all top-division teams (FBS, I-A, University Division, and pre-1937 major programs).

The original scraper (`alltimegames.py`) targeted [CFB Data Warehouse](http://cfbdatawarehouse.com/), which is now defunct. The data file is maintained directly.

## Design

Based on [FiveThirtyEight's NFL Elo](http://fivethirtyeight.com/datalab/nfl-elo-ratings-are-back/), adapted for college football's open/conference system. Games involving non-top-division opponents are discarded (like FIFA disregarding friendlies). Teams that later returned to the top division retain their Elo across absences.

Parameters:
- **K** = 17
- **C** = 2.2
- **P** = 0.001
- **INIT** = 1000
- **REG** = 1/4 (regression toward mean during offseason)

## Usage

```bash
pip install -e ".[dev]"
python -c "from elo import do_all_elo; do_all_elo()"
```

Outputs `allgames.csv` with updated Elo values and `Elo.csv` with season-by-season ratings.

## Key Files

| File | Purpose |
|------|---------|
| `elo.py` | Elo engine: `do_all_elo()` to run, `show_all()` to plot |
| `alltimegames.py` | Original scraper (defunct — CFB Data Warehouse down) |
| `teams.py` | ~428 teams with top-division year ranges through 2026 |
| `allgames.csv` | ~76K games in 10-column CSV format |
| `Elo.csv` | Season-by-season team ratings |
| `pyproject.toml` | Project config and dependencies |
