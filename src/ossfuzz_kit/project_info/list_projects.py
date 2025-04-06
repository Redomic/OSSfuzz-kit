from functools import lru_cache
from requests.exceptions import RequestException

from ossfuzz_kit.utils import fetch_from_url, shallow_clone_repo
from ossfuzz_kit.config import OSS_FUZZ_REPO_URL, CLONE_DEPTH, GIT_TREE_API_URL, DEFAULT_HEADERS

@lru_cache(maxsize=1)
def list_all_projects(use_fallback: bool = True) -> list[str]:
    """
    Returns a sorted list of all OSS-Fuzz project names.

    - Prioritizes local shallow clone from disk.
    - Falls back to GitHub Tree API if `use_fallback` is True and local fails.
    - Uses LRU cache for efficiency.
    """

    try:
        repo_path = shallow_clone_repo(OSS_FUZZ_REPO_URL, CLONE_DEPTH)
        if not repo_path.exists():
            raise FileNotFoundError("Could not find `projects/` directory in the shallow clone.")

        project_names = [p.name for p in repo_path.iterdir() if p.is_dir()]
        return sorted(project_names)

    except Exception as e:
        print(f"[Warning] Local clone failed: {e}")

        if use_fallback:
            try:
                response = fetch_from_url(url=GIT_TREE_API_URL, format="json")
                tree = response.get("tree", [])

                project_names = {
                    entry["path"].split("/")[1]
                    for entry in tree
                    if entry["path"].startswith("projects/")
                    and entry["type"] == "tree"
                    and len(entry["path"].split("/")) == 2
                }
                return sorted(project_names)

            except RequestException as api_err:
                raise RuntimeError(f"GitHub API failed, please check your connection: {api_err}") from api_err

        raise RuntimeError("Failed to retrieve project list from both local and API.")