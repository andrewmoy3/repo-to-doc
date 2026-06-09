from __future__ import annotations

import glob
import logging
import os
import subprocess
from pathlib import Path

import requests

from dotenv import load_dotenv

log = logging.getLogger(__name__)
load_dotenv()  # Load environment variables from .env file 


def discover_local(local_patterns: list[str]) -> list[dict]:
    """
    Given a list of folder paths, find all git repositories and return their information in the same format as discover_github.

    Arguments:
        local_patterns: List of folder paths to search for local git repositories.

    Returns:
        A list of dictionaries with each entry containing information about a repository.
    """
    def get_head_sha(repo_path: Path) -> str | None:
        """
        Returns the SHA of the HEAD commit for a given repository path, or None if it cannot be determined.

        Argument: repo_path: Path to the local git repository.
        """
        try:
            result = subprocess.run(
                # run git rev-parse HEAD, return the output as a string
                ["git", "rev-parse", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None


    repos = []
    for pattern in local_patterns:# for each glob pattern
        for path_str in glob.glob(os.path.expanduser(pattern)): # fidn matching glob patterns and expand the full path
            path = Path(path_str)

            # if the path is a file, skip
            if path.is_file():
                continue

            # if the path is a directory and does not contain a .git folder, skip
            if not (path / ".git").exists():
                log.warning("Path %s is not a git repository, skipping", path)
                continue

            # Reads the SHA for the HEAD of the repository, skips if it does not exist
            sha = get_head_sha(path)
            if sha is None:
                log.warning("Could not read HEAD for %s, skipping", path)
                continue

            # log/return repo info
            repos.append({"name": path.name, "path": path, "sha": sha})
            log.debug("Found local repo %s @ %s", path.name, sha[:7])
    return repos


def discover_github(token: str) -> list[dict]:
    """
    Given a GitHub token, fetches the remote repositories from GitHub and returns a list of dictionaries with repository information.

    Arguments:
        token: GitHub token to authenticate API requests.

    Returns:
        A list of dictionaries with each entry containing information about a GitHub repository.
    """
    headers = {"Authorization": f"Bearer {token}"}
    repos = []

    page = 1
    # Loop through all return pages until we get an empty response
    while True:
        r = requests.get(
            "https://api.github.com/user/repos",
            headers=headers,
            params={"per_page": 100, "page": page, "type": "all"},
        )
        if r.status_code == 401:
            log.warning("Invalid GitHub token, skipping GitHub discovery")
            return []
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break # no more repos to fetch
        repos.extend(batch) # add the current batch of repos to the list
        page += 1

    log.info("Found %d repos on GitHub", len(repos))

    # return all repos with relavant information
    return [
        {"name": r["name"], "path": None, "sha": r["pushed_at"], "clone_url": r["clone_url"]}
        for r in repos
    ]


def discover(
    local_patterns: list[str] | None = None,
    github_token: str | None = None,
) -> list[dict]:
    """
    Discovers repositories from the local filesystem and pulls from GitHub. 

    Arguments (both optional):
        local_patterns: List of glob patterns to search for local git repositories.
        github_token: GitHub token to authenticate API requests. If not provided, will look for the GITHUB_TOKEN environment variable.

    Returns:   
        A list of dictionaries with each entry containing information about a repository.
    """
    repos = []

    if local_patterns:
        repos.extend(discover_local(local_patterns))

    token = github_token or os.environ.get("GITHUB_TOKEN")
    if token:
        repos.extend(discover_github(token))

    log.info("Discovered %d repos total", len(repos))
    return repos
