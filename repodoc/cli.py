from __future__ import annotations

import logging
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

        # optional github token accepts a string. If not provided, will look for the GITHUB_TOKEN environment variable
        parser.add_argument("--token", help="GitHub token to authenticate API requests. If not provided, will look for the GITHUB_TOKEN environment variable.")

        # optional local patterns accepts a list of strings/glob patterns
        parser.add_argument("-l", "--local", nargs="*", help="Glob patterns to search for local git repositories.")

        return parser

    parser = create_cli_interface()
    args = parser.parse_args()

    # discover repos from local and github using CLI arguments
    log.info("Starting repository discovery with local patterns: %s and GitHub token: %s", args.local, "provided" if args.token else "not provided")
    repos = discover(local_patterns=args.local, github_token=args.token)
    
    # delete unchanged repositories
    log.info("Removing unchanged repositories from the list of discovered repositories")
    repos = remove_unchanged_repos(repos)

    # scan the discovered repositories to gather information deterministically
    log.info("Scanning repositories for information")
    scan(repos)

    # passing information to LLM to generate documentation
    # log.info("Generating documentation for repositories using LLM")
    # gen_docs(repos)

    # writing documentation to file system
    # log.info("Writing generated documentation to file system")
    # write(repos)

if __name__ == "__main__":
    main()
