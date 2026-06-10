# repodoc

A command line Python tool that converts local/GitHub git repositories into Markdown project overviews. Designed for personal use in Obsidian to integrate with manually typed notes and resources.

## Setup

Requires Python 3.10+.

```bash
pip install -e .
cp .env.example .env
```

1. Enter Anthropic API Key in `.env` to enable LLM summaries (other APIs, local models not yet supported)
2. Enter GitHub personal access token in `.env` for access to your private repos (can also pass token via command line argument at run time)
    - To generate GitHub PAT: 
    - Go to GitHub > Settings > Developer settings > Personal access tokens
    - Generate fine-grained token with repository access to all repos you want to document

## Usage

### Basic Usage

If both API keys are provided in `.env`, generate project overview markdown files for all remote GitHub repositories by navigating to the project root and running:

```bash
python repodoc/cli.py -e
```

.md files will be saved to `repodoc_output/` in the project root

### Command Line Arguments

| Argument | Purpose | Number Arguments | Notes |
|---|---|---|---|
| `-e`, `--env` | Load GitHub PAT from `.env`, specify specific remote repos by name | (0, $\infty$)| If no arguments passed, loads/documents all accessible GitHub repos.|
| `--token` | Pass GitHub PAT manually via command line | (1) | Overrides `--env` |
| `-l`, `--local` | Path to local repositories (glob pattern) | (1, $\infty$) |  |
| `-o`, `--output` | Output folder path | (1) | Default folder is `repodoc_output/` in the project root  |
| `-f`, `--force` | Ignore state, force regenerate repo docs| 0 |  |

### Example commands

```bash
# Generate docs for all GitHub repos using token from .env
python repodoc/cli.py -e

# Generate docs for specific GitHub repos by name using token from .env
python repodoc/cli.py -e repo1 repo2

# Generate docs for all GitHub repos to a custom output folder
python repodoc/cli.py -e --output path/to/vault/

# Generate docs for all GitHub repos using token from command line
python repodoc/cli.py --token FAKE_TOKEN

# Generate docs for repo1, repo2 using token from command line
python repodoc/cli.py --token FAKE_TOKEN -e repo1 repo2

# Generate docs for local repos matching glob pattern
python repodoc/cli.py -l "/path/to/repos/*"

# Force full rebuild of all remote repos
python repodoc/cli.py -e --force

# Force full rebuild of remote repos named repo1 and repo2
python repodoc/cli.py -e repo1 repo2 --force
```
-----------------------------------------------------------

## Environment variables

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Enable LLM summaries (omit to use offline stub) |
| `GITHUB_TOKEN` | Higher API rate limits and access to private repos |

## Output

```
<vault>/.repodoc-state.json                   # incremental SHA state
<project_root>/repodoc_output/                # default output folder
```

Re-runs only regenerate notes for repos whose HEAD SHA has changed since the last run. Manual edits to notes are preserved outside the auto-generated region.
