# repodoc

Turns GitHub repositories into Obsidian project overviews — one overview note per repo, one module note per top-level folder, joined by `[[wikilinks]]` and a Map of Content.

## Install

Requires Python 3.10+.

```bash
pip install -e .
```

## Usage

------------------- implement later -----------------------
```bash
# Scan local repos matching a glob
repodoc --vault ~/ObsidianVault --local "~/code/*"

# Also pull repos from GitHub
repodoc --vault ~/ObsidianVault --github YOUR_USERNAME --local "~/code/*"

# Force full rebuild (ignore incremental state)
repodoc --vault ~/ObsidianVault --local "~/code/*" --force

# Verbose logging
repodoc --vault ~/ObsidianVault --local "~/code/*" -v

# Without installing
python -m repodoc.cli --vault ~/ObsidianVault --local "~/code/*"
```
-----------------------------------------------------------

## Environment variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Enable LLM summaries (omit to use offline stub) |
| `GITHUB_TOKEN` | Higher API rate limits and access to private repos |

## Output

```
<vault>/Projects/_Projects MOC.md             # links all projects
<vault>/Projects/<repo>/<repo>.md             # overview note
<vault>/Projects/<repo>/<repo>---<module>.md  # one per top-level folder
<vault>/.repodoc-state.json                   # incremental SHA state
<vault>/.repodoc.log                          # run log
```

Re-runs only regenerate notes for repos whose HEAD SHA has changed since the last run. Manual edits to notes are preserved outside the auto-generated region.
