# real_repo_1

## What this is
A strikeout prediction system that models pitcher and hitter performance using historical MLB statcast data to predict strikeout outcomes.

## How it works
Raw statcast data (2015-2025) is pulled into parquet files, then processed into a DuckDB database. Separate pitcher and hitter tables are built with player identifiers, names, and pitch counts. The main prediction logic lives in `db_funcs/get_player_data.py` to query player stats from the database.

## Key files / entry points
- `scripts/get_raw_data.py` — fetches statcast data
- `scripts/make_raw_duckdb.py` — converts parquet to DuckDB
- `scripts/make_pitchers_table.py` / `scripts/make_hitters_table.py` — builds the pitcher/hitter lookup tables
- `src/k_predictor/db_funcs/get_player_data.py` — core query logic
- `src/k_predictor/paths.py` — path configuration

## Tech stack
Python, DuckDB (database), parquet (raw data storage), editable pip install via pyproject.toml

## What to remember
- Project uses editable install (`pip install -e .`) — changes to `src/` reflect immediately
- Data pipeline: raw parquets → DuckDB → player tables
- The `notepad/` folder is scratch work (duck.py, pandas_test.py, test.py) — can probably ignore
- Recently restructured the project layout; paths.py handles the config

## Current state
In progress — infrastructure is set up, data pipeline working, but the actual prediction model logic seems incomplete

## What's next
Need to build out the actual strikeout prediction model using the pitcher/hitter tables. The database and player lookup functions are ready to consume.

## Related projects
None noted in the repo.