# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this project is

A CLI that turns GitHub repositories into Obsidian project overview markdown files.

**The point is not "generate documentation."** The task being automated is *re-reading
your own code to remember what it does* — a recurring, manual chore that happens
every time I revisit an old project. Keep this framing in mind: the audience for
generated notes is *one person (the author) six months from now*, optimized for
recall and cross-project navigation, not for onboarding a stranger. Do not turn
this into a README generator or a public-docs tool.

## Architecture (data flow)

```
discover.py  → find repos (local + GitHub API), get SHAs
state.py     → removes unchanged repos based on SHA, saves state
scan.py      → deterministic, language-agnostic structure extraction
generate.py → LLM writes prose from the structure of the codebase (scan.py output)
write.py     → render Obsidian notes with idempotent managed regions + MOC

cli.py       → orchestrates the 5 modules: discover → state → scan → generate → write
```

Each module is small and single-purpose (~100 lines). Preserve that separation;
do not merge stages or add cross-stage coupling.

## Non-negotiable design decisions

These are the project's reason for existing. Do not "simplify" them away — they
are the difference between this and a naive 15-line `llm(open(file).read())`
script. If a change would undermine one, stop and flag it.

1. **Deterministic skeleton, LLM for prose only.** `scan.py` extracts the file
   tree, language stats, and dependency manifests in code. Only send that summary 
   to the LLM, not raw code, which will blow up the context window.

2. **Language-agnostic scanning.** No per-language AST parsing. Detection is by
   file extension + dependency manifests + signal files, so it works across
   Python/Java/C++/JS/etc. WITHOUT having to interpret language from raw code.
   If adding language support, extend the `EXT_LANG` /
   `MANIFESTS` maps in `scan.py`; do not add a language-specific parser without
   discussing it. 

3. **Idempotent writes (managed regions).** Generated content lives between
   `<!-- repodoc:auto:start -->` and `<!-- repodoc:auto:end -->` markers in each
   note. Re-runs replace ONLY that block so that the user can add manual notes that
   won't be changed by the LLM. Any new writer code MUST go through `write._write_idempotent`.

4. **Incremental by SHA.** `state.py` stores each repo's last-processed HEAD SHA;
   unchanged repos are skipped. `--force` overrides. Keep re-runs cheap.

5. **Fault isolation.** A repo that fails to process is logged and skipped — one
   bad repo must never abort the whole run.  

## Commands

```bash
# Install (editable)
pip install -e .
cp .env.example .env

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
`
```
Environment variables: `ANTHROPIC_API_KEY` (summaries; omit for stub mode),
`GITHUB_TOKEN` (higher API rate limits / private repos).

## Testing
Always verify these four behaviors after touching the pipeline: discovery,
incremental skip, idempotent writes (manual edits preserved), fault isolation.

## Conventions

- Python 3.10+; standard library first, minimal deps (`requests`, `anthropic`).
- Logging via the `logging` module, never `print` (except final CLI status).
- Module-level `log = logging.getLogger(__name__)`.
- Type hints with `from __future__ import annotations`.
- Keep modules single-purpose and under ~120 lines.

## Known limitations / roadmap (don't silently "fix" by overreaching)

- "On new repo created" trigger needs a webhook or template repo; a push event
  can't observe repo creation. The included GitHub Action is the per-repo
  freshness layer only.
- No `tree-sitter` symbol extraction yet (deliberate scope choice).
- No test suite yet — add `pytest` tests before large refactors.
- Future: RAG over the generated vault. The structured markdown + consistent
  frontmatter is intentionally a clean corpus for this; preserve frontmatter
  consistency in `write.py` so that stays true.
```
