

def scan(repos):
    """
    Accepts a list of repositories (both local and GitHub) and gathers deterministic information about each individual repo. Checks if an update is necessary by comparing the SHA of the HEAD commit to the latest version.

    Arguments:
        repos: A list of dictionaries containing information about repositories, including local and GitHub repositories.

    Returns:
        A list of dictionaries with detailed information about each repository.
    """
    print("\nScanning repositories:")

    for repo in repos:
        name, path, sha, clone_url = repo.get("name"), repo.get("path"), repo.get("sha"), repo.get("clone_url")

        # scan local repo if path exists, else scan remote github repo
        if path is not None: 
            print(f"Scanning local repository {name} at {path} with SHA {sha}")
        else:
            print(f"Scanning remote GitHub repository {name} with last push SHA {sha} and clone URL {clone_url}")
