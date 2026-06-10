# real_repo_2

## What this is
Scrapes Division 3 baseball game data to generate spray charts for individual players, helping coaches visualize hitting tendencies and make fielding decisions.

## How it works
1. Scrape box score links from a team's schedule
2. Parse roster data into a pandas database
3. Aggregate play-by-play data from all box scores into a CSV
4. Parse and analyze the play-by-play to categorize hits by type
5. Generate spray chart images for each player
6. Combine all player charts into a PDF

## Key files / entry points
- `main.py` — entry point, orchestrates the pipeline
- `funcs/get_boxscore_links.py` — scrapes schedule for game links
- `funcs/get_play_by_play.py` — aggregates play-by-play data
- `funcs/create_chart_image.py` — generates individual spray chart images
- `funcs/stitch_to_pdf.py` — combines images into final PDF

## Tech stack
- Python (8 files)
- pandas (inferred from roster handling)
- Web scraping (BeautifulSoup or similar, inferred from scraping functions)
- Image processing (PIL/Pillow, inferred from chart generation)

## What to remember
- Recent commits show I was distinguishing between hit types — make sure that logic is working correctly
- Two roster files exist (standard + AI version) — check which one you're using
- The Gettysburg roster is the test data with 11 players

## Current state
In progress — hit type distinction was the last feature being added

## What's next
Verify hit type categorization is working end-to-end through the spray chart generation

## Related projects
Built for Swarthmore College baseball team originally; mentions watching it applied to other Division 3 teams (Gettysburg data present)