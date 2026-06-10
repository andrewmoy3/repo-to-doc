# real_repo_2

# real_repo_2

## What this is
Scrapes Division 3 baseball game data to generate spray charts visualizing each player's hitting tendencies, helping coaches with fielding decisions.

## How it works
1. Scrape boxscore links from a team's schedule
2. Fetch roster data and play-by-play info from those boxscores
3. Aggregate play-by-play into a CSV and parse it
4. Generate individual spray chart images for each player
5. Combine all player charts into a PDF

## Key files / entry points
- **main.py** — entry point, orchestrates the pipeline
- **funcs/get_boxscore_links.py** — scrapes schedule for boxscore URLs
- **funcs/get_play_by_play.py** — aggregates play-by-play data
- **funcs/create_chart_data.py** and **create_chart_image.py** — generates individual spray charts
- **funcs/stitch_to_pdf.py** — combines charts into PDF

## Tech stack
Python (8 files); pandas for data handling; web scraping (exact library unclear from data); image generation and PDF stitching

## What to remember
- There are two roster approaches: standard (`get_roster.py`) and AI-based (`get_roster_ai.py`) — check which one is being used
- Recent work distinguished between hit types, so the chart logic may be more nuanced now
- Sample data is for Gettysburg team; adjust domain/team name as needed for other schools

## Current state
Working — has example output and completed MVP flow

## What's next
Last commits added hit-type distinction; check if that's fully integrated into the chart generation

## Related projects
Inspired by involvement with Swarthmore College baseball team