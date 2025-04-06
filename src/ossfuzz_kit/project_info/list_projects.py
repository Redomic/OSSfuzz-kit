from functools import lru_cache
import logging
from requests.exceptions import RequestException

from ossfuzz_kit.utils import fetch_from_url, get_repo_manager
from ossfuzz_kit.config import GIT_TREE_API_URL

logger = logging.getLogger("ossfuzz_kit")

@lru_cache(maxsize=1)
def list_all_projects(use_fallback: bool = True) -> list[str]:
    """
    Returns a sorted list of all OSS-Fuzz project names.

    - Prioritizes local shallow clone from disk.
    - Falls back to GitHub Tree API if `use_fallback` is True and local fails.
    - Uses LRU cache for efficiency.
    """

    try:
        manager = get_repo_manager()
        repo_path = manager.get_projects_dir()

        if not repo_path.exists():
            raise FileNotFoundError("Could not find `projects/` directory in the local clone.")

        project_names = [p.name for p in repo_path.iterdir() if p.is_dir()]
        return sorted(project_names)

    except Exception as e:
        logger.warning(f"Local clone failed when listing projects: {e}")

        if use_fallback:
            logger.debug("Falling back to GitHub Tree API for project list...")
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