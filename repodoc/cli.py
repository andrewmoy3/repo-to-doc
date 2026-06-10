from __future__ import annotations

import logging
import os
from repodoc.discover import discover
from repodoc.state import remove_unchanged_repos
from repodoc.scan import scan
import argparse

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    def create_cli_interface():
        """
        Creates parser, defines cli arguments with `--help` descriptions
        """
        parser = argparse.ArgumentParser(description="Discover git repositories locally and on GitHub.")
        # optional flag that lets program use GITHUB_TOKEN environment variable
        parser.add_argument("-e", "--env", nargs="*", help="Use GITHUB_TOKEN environment variable for GitHub discovery. Specify remote repos by name to limit discovery (default behavior discovers all remote repos).")

        # optional github token accepts a string. 
        parser.add_argument("--token", help="Pass GitHub token to authenticate API requests. Overrides --env if both are provided.")

        # optional local patterns accepts a list of strings/glob patterns
        parser.add_argument("-l", "--local", nargs="*", help="Glob patterns to search for local git repositories.")

        return parser

    parser = create_cli_interface()
    args = parser.parse_args()

    # discover repos from local and github using CLI arguments
    token = os.environ.get("GITHUB_TOKEN") if args.env is not None else args.token
    log.info("\nDISCOVERY: Starting repository discovery with local patterns: %s and GitHub token: %s", args.local, "provided" if token else "not provided")
    print(args.env)
    repos = discover(local_patterns=args.local, github_token=token, specified_repos=args.env)
    
    # delete unchanged repositories
    log.info("\nSTATE DETECTION: Removing unchanged repositories from the list")
    repos = remove_unchanged_repos(repos)
    log.info("%d repositories have changed and will be scanned", len(repos))
    for repo in repos:
        log.info("- %s", repo["name"])

    # TEMPORARY -- remove state file after each run for testing purposes
    from pathlib import Path
    state_file = Path(__file__).parent.parent / ".repodoc-state.json"
    if state_file.exists():
        state_file.unlink()
    #############

    # scan the discovered repositories to gather information deterministically
    log.info("\nEXTRACT INFO: Scanning repositories for information")
    scan(repos)

    # passing information to LLM to generate documentation
    log.info("\nGENERATING DOCUMENTATION: Generating documentation for repositories using LLM")
    # gen_docs(repos)

    # writing documentation to file system
    # log.info("\nWRITING TO FILES: Writing generated documentation to file system")
    # write(repos)

if __name__ == "__main__":
    main()
