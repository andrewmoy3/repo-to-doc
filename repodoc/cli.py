from __future__ import annotations

import logging
from repodoc.discover import discover
import argparse

logging.basicConfig(level=logging.INFO, format="%(message)s")


def main():
    def create_cli_interface():
        """
        Creates parser, defines cli arguments with `--help` descriptions
        """
        parser = argparse.ArgumentParser(description="Discover git repositories locally and on GitHub.")

        # add -l as shorthand
        parser.add_argument("--token", help="GitHub token to authenticate API requests. If not provided, will look for the GITHUB_TOKEN environment variable.")
        parser.add_argument("-l", "--local", nargs="*", help="Glob patterns to search for local git repositories.")
        return parser

    parser = create_cli_interface()
    args = parser.parse_args()
    print(args)
    print("Discovering repositories...")
    for r in discover(local_patterns=args.local, github_token=args.token):
        print(r["name"])

if __name__ == "__main__":
    main()
