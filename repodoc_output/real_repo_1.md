# real_repo_1

# real_repo_1

## What this is
A strikeout prediction model that analyzes baseball statcast data to predict pitcher strikeouts based on hitter and pitcher characteristics.

## How it works
I'm ingesting raw statcast data (2015-2025) into a DuckDB database, then building separate hitter and pitcher tables with aggregated pitch statistics. The predictor likely uses these tables to make strikeout predictions.

## Key files / entry points
- `scripts/get_raw_data.py` — fetches raw statcast data
- `scripts/make_raw_duckdb.py` — loads parquet files into DuckDB
- `scripts/make_hitters_table.py` & `scripts/make_pitchers_table.py` — builds aggregated player tables
- `src/k_predictor/db_funcs/get_player_data.py` — queries player data from DB

## Tech stack
Python, DuckDB (for data storage), Parquet (raw data format), setuptools (editable install via pyproject.toml)

## What to remember
- This is set up as an editable install (`pip install -e .`), so changes to src are live
- Data flows: raw parquets → DuckDB → player tables
- There's a `notepad/` directory with test scripts—check those if I need to debug individual pieces
- The project was recently restructured (src layout reorganized, paths.py moved)

## Current state
In progress — infrastructure is in place (data fetching, DB setup, player tables), but the actual prediction model isn't visible yet

## What's next
Build out the actual strikeout prediction logic, probably in src/k_predictor/. Need to define what features go into the model and train/test it.

## Related projects
None visible in the repo data