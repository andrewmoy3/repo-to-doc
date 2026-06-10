from __future__ import annotations

import logging
import os
from repodoc.discover import discover
from repodoc.state import remove_unchanged_repos
from repodoc.scan import scan
from repodoc.generate import gen_docs
from repodoc.write import write
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

        # optional output folder path for generated documentation
        parser.add_argument("-o", "--output", help="Output folder path for generated documentation (default: repodoc_output/).", default="repodoc_output/")

        # optional flag to force full rebuild of specified repos, ignoring incremental state
        parser.add_argument("-f", "--force", action="store_true", help="Force full rebuild, ignoring incremental state. Specify repo names to limit to specific repos (default behavior forces rebuild of all discovered repos).")

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
    repos = remove_unchanged_repos(repos, force=args.force)
    log.info("%d repositories have changed and will be scanned", len(repos))

    # loop through repos to scan, generate documentation, and write to file system
    for repo in repos:
        log.info("\n\n==============================")
        log.info("PROCESSING %s", repo["name"])
        # scan the discovered repositories to gather information deterministically
        log.info("\nEXTRACT INFO: Scanning repository for information")
        scanned_repo = scan(repo)

        # passing information to LLM to generate documentation
        log.info("\nGENERATING DOCUMENTATION: Generating documentation for repository using LLM")
        document = gen_docs(scanned_repo)

        # writing documentation to file system
        output_path = args.output
        log.info("\nWRITING TO FILES: Writing generated documentation to %s", output_path)
        write(document, output_path)

    # TEMPORARY -- remove state file after each run for testing purposes
    # from pathlib import Path
    # state_file = Path(__file__).parent.parent / ".repodoc-state.json"
    # if state_file.exists():
    #     state_file.unlink()
    #############

if __name__ == "__main__":
    main()
