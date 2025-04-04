from os import path
import requests
from functools import lru_cache
from requests.exceptions import RequestException

from ossfuzz_kit.utils import shallow_clone_repo
from ossfuzz_kit.config import OSS_FUZZ_REPO_URL, CLONE_DEPTH, GIT_TREE_API_URL, DEFAULT_HEADERS

@lru_cache(maxsize=1)
def list_all_projects() -> list[str]:
    """
    Lists all OSS Fuzz projects by parsing the GitHub Tree API:
    - Falls back to shallow cloning if the API fails.
    - Uses LRU caching for performance.
    """
    try:
        response = requests.get(GIT_TREE_API_URL, headers=DEFAULT_HEADERS, timeout=15)
        response.raise_for_status()

        tree = response.json().get("tree", [])

        project_names = {
            entry["path"].split("/")[1]
            for entry in tree
            if entry["path"].startswith("projects/")
            and entry["type"] == "tree"
            and len(entry["path"].split("/")) == 2
        }
        return sorted(project_names)

    except RequestException as e:
        print(f"[Warning] Git Tree API failed ({e}). Falling back to local clone...")

        repo_path, tmpdir = shallow_clone_repo(OSS_FUZZ_REPO_URL, CLONE_DEPTH)
        projects_dir = repo_path / "projects"

        if not projects_dir.exists():
            raise FileNotFoundError("Could not find `projects/` directory in the cloned repo.")

        project_names = [p.name for p in projects_dir.iterdir() if p.is_dir()]
        tmpdir.cleanup()
        return sorted(project_names)