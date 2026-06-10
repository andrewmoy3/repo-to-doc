import json
import os
from pathlib import Path

import logging
log = logging.getLogger(__name__)

def remove_unchanged_repos(repos: list[dict], force: bool) -> list[dict]:
    """
    Checks if an update is necessary by comparing the SHA of the HEAD commit to the latest version. Keeps a JSON state file in the root of the project with an entry for each repository. If the SHAs match, removes that repo from the list. Returns the list of repositories that need to be updated.

    Arguments:
        repos: A list of dictionaries containing information about repositories, including local and GitHub repositories.

    Returns:
        A list of dictionaries with information about repositories that have changed and need to be updated.
    """
    # define .repodoc-state.json file path at root of the project
    STATE_FILE = Path(__file__).parent.parent / ".repodoc-state.json"

    # create state file if it doesn't exist
    if not STATE_FILE.exists():
        STATE_FILE.touch()
        STATE_FILE.write_text(json.dumps({}))

    ret_repos = []

    # read state file
    with open(STATE_FILE, "r") as f:
        state = json.load(f)

    for repo in repos:  
        name = repo.get("name")
        sha = repo.get("sha")
        path = str(repo.get("path", None))
        clone_url = repo.get("clone_url", None)

        if name not in state:
            # if repo not in state, add it to state and return list
            state[name] = {"sha": sha, "path": path, "clone_url": clone_url}
            ret_repos.append(repo)
        else:
            # if repo IS in state, compare SHAs. If they match, skip. If they don't match, update state and return list
            # if force is True, skip SHA comparison and return all repos
            if state[name]["sha"] != sha:
                log.info("Repository '%s' has changed (SHA: %s -> %s)", name, state[name]["sha"], sha)
                state[name] = {"sha": sha, "path": path, "clone_url": clone_url}
                ret_repos.append(repo)
            elif force:
                log.info("Force flag is set. Updating repository '%s'.", name)
                state[name] = {"sha": sha, "path": path, "clone_url": clone_url}
                ret_repos.append(repo)
            else: # (state[name]["sha"] == sha)
                log.info("Repository '%s' has not changed: skipping", name)
    f.close()
    # write updated state back to file
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

    return ret_repos
