from __future__ import annotations

import os
import subprocess
from pathlib import Path

import requests

# skip these folders when scanning
SKIP_DIRS = {".git", "__pycache__", "node_modules", ".venv", "dist", "build"}

# map file extensions to file types
EXT_LANG = {
    ".py": "Python",
    ".ts": "TypeScript",
    ".js": "JavaScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".rb": "Ruby",
    ".sh": "Shell",
}

SIGNALS = {"Dockerfile", "docker-compose.yml", "Makefile", ".github"}

def _scan_local(repo_path: Path) -> dict:
    """
    Scans a local repository to extract information such as file types, folder structure, README contents, dependency files, and git commit messages.

    Arguments:
        repo_path: Path to the local git repository.

    Returns:
        A dictionary containing the extracted information about the repository.
    """
    file_tree = []
    lang_counts = {}
    signal_files = []
    dependencies = []
    readme = None

    MANIFEST_FILES = {"package.json", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "pyproject.toml"}

    # for all files and folders:
    for path in repo_path.rglob("*"):
        # skip if in SKIP_DIRS
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        if path.is_file():
            rel = str(path.relative_to(repo_path))
            file_tree.append(rel)
            lang = EXT_LANG.get(path.suffix)
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
            if path.name in MANIFEST_FILES:
                dependencies.append(path.name)
            if path.name in {"README.md", "README.txt"} and path.parent == repo_path:
                readme = path.read_text(errors="ignore")
        if path.name in SIGNALS:
            signal_files.append(path.name)

    top_level_modules = [
        p.name for p in sorted(repo_path.iterdir())
        if p.is_dir() and not p.name.startswith(".") and p.name not in SKIP_DIRS
    ]

    # get all commit messages
    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%s"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True,
        )
        commit_messages = result.stdout.splitlines()
    except subprocess.CalledProcessError:
        commit_messages = []

    return {
        "name": repo_path.name,
        "file_tree": sorted(file_tree),
        "languages": lang_counts,
        "top_level_modules": top_level_modules,
        "signal_files": signal_files,
        "dependencies": dependencies,
        "readme": readme,
        "commit_messages": commit_messages,
    }


def _scan_remote(name: str, clone_url: str) -> dict:
    """
    Scans a remote GitHub repository via the API without cloning.

    Arguments:
        name: Repository name.
        clone_url: GitHub clone URL (used to derive owner/repo for API calls).

    Returns:
        A dictionary containing the extracted information about the repository.
    """
    token = os.environ.get("GITHUB_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}

    # derive owner/repo from clone_url: https://github.com/owner/repo.git
    parts = clone_url.rstrip(".git").rstrip("/").split("/")
    owner, repo = parts[-2], parts[-1]

    # fetch full file tree
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/git/trees/HEAD",
        headers=headers,
        params={"recursive": "1"},
    )
    if r.status_code != 200:
        return {"name": name, "error": f"GitHub API returned {r.status_code}"}

    tree = r.json().get("tree", [])
    file_tree = [item["path"] for item in tree if item["type"] == "blob"]

    lang_counts = {}
    dependencies = []
    signal_files = []
    MANIFEST_FILES = {"package.json", "requirements.txt", "go.mod", "Cargo.toml", "pom.xml", "pyproject.toml"}

    for path_str in file_tree:
        path = Path(path_str)
        if any(skip in path.parts for skip in SKIP_DIRS):
            continue
        lang = EXT_LANG.get(path.suffix)
        if lang:
            lang_counts[lang] = lang_counts.get(lang, 0) + 1
        if path.name in MANIFEST_FILES:
            dependencies.append(path.name)
        if path.name in SIGNALS:
            signal_files.append(path.name)

    # fetch README from root if it exists
    readme = None
    for readme_name in ("README.md", "README.txt"):
        if readme_name in file_tree:
            r = requests.get(
                f"https://api.github.com/repos/{owner}/{repo}/contents/{readme_name}",
                headers={**headers, "Accept": "application/vnd.github.raw"},
            )
            if r.status_code == 200:
                readme = r.text
            break

    # fetch commit messages
    commit_messages = []
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/commits",
        headers=headers,
        params={"per_page": 100},
    )
    if r.status_code == 200:
        commit_messages = [c["commit"]["message"].splitlines()[0] for c in r.json()]

    top_level_modules = sorted({
        Path(p).parts[0] for p in file_tree
        if len(Path(p).parts) > 1 and Path(p).parts[0] not in SKIP_DIRS
    })

    return {
        "name": name,
        "file_tree": sorted(file_tree),
        "languages": lang_counts,
        "top_level_modules": top_level_modules,
        "signal_files": signal_files,
        "dependencies": dependencies,
        "readme": readme,
        "commit_messages": commit_messages,
    }


def scan(repo, output_path):
    """
    Accepts a repository dict (both local and GitHub) and gathers deterministic information about each individual repo. 

    Arguments:
        repo: A dictionary containing information about repositories, including local and GitHub repositories.

    Returns:
        A dictionary with detailed information about the repository. Fields include:
        Repository Name
        Languages (with counts)
        Top Level Modules (folders in the root of the repo)
        Signal Files (presence of Dockerfile, Makefile, .github, etc.)
        File Tree (list of all files in the repo)
        README Contents (if README.md or README.txt exists, return the contents)
        Dependency Files (presence of package.json, requirements.txt, go.mod, etc.)
        All Git Commit Messages
        Existing note (with manual info) if it exists 
    """
    name, path, sha, clone_url = repo.get("name"), repo.get("path"), repo.get("sha"), repo.get("clone_url")

    # scan local repo if path exists, else scan remote github repo
    if path is not None:
        print(f"Scanning local repository {name} at {path}")
        scanned_repo = _scan_local(Path(path))
    else:
        print(f"Scanning remote GitHub repository {name}")
        scanned_repo = _scan_remote(name, clone_url)

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    existing_note_path = output_path / f"{name}.md"
    if existing_note_path.exists():
        scanned_repo["existing_note"] = existing_note_path.read_text()

    return scanned_repo
