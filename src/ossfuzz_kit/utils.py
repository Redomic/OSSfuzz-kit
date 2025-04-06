import subprocess
import time
import sys
import requests
import logging
from urllib.parse import urlparse
from tqdm import tqdm
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta
from requests.exceptions import RequestException

from ossfuzz_kit.config import OSS_FUZZ_REPO_URL, CLONE_DEPTH, DEFAULT_TIMEOUT, DEFAULT_HEADERS

logger = logging.getLogger("ossfuzz_kit")

class FetchError(Exception):
    """Raised when a URL fetch fails."""
    pass

def fetch_from_url(
    url: str,
    headers: dict = None,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = 3,
    format: str = "text",
) -> str:
    """
    Fetches raw text content from a URL with retries and exponential backoff.
    """
    backoff_factor = 0.5
    headers = headers or DEFAULT_HEADERS

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            if format == "text":
                return response.text
            elif format == "json":
                return response.json()
            elif format == "bytes":
                return response.content
            else:
                raise ValueError(f"Unsupported format: {format}")

        except RequestException as e:
            if attempt == max_retries:
                raise FetchError(f"Failed to fetch {url} after {max_retries} attempts: {e}")
            wait_time = backoff_factor * (2 ** (attempt - 1))
            logger.warning(f"[Retry {attempt}] Failed to fetch {url}. Retrying in {wait_time:.1f}s...")
            time.sleep(wait_time)

def shallow_clone_repo(repo_url: str, depth: int = 1, sparse_dir: str = "projects") -> Path:
    """
    Shallow clones a git repository and returns the path to the clone.
    """
    dest_dir = "data/oss-fuzz"
    clone_path = Path(dest_dir)

    if (clone_path / sparse_dir).exists():
        return clone_path / sparse_dir

    clone_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Cloning {repo_url} (sparse: '{sparse_dir}')...")

        with tqdm(total=2, desc="Cloning repo", unit="step", file=sys.stdout) as pbar:
            subprocess.run(
                ["git", "clone", "--depth", str(depth), "--filter=blob:none", "--sparse", repo_url, str(clone_path)],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pbar.update(1)

            subprocess.run(
                ["git", "-C", str(clone_path), "sparse-checkout", "set", sparse_dir],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pbar.update(1)

        return clone_path / sparse_dir

    except subprocess.CalledProcessError as e:
        logger.error(f"Git clone failed... Check your connection")
        raise RuntimeError(f"Git clone failed: {e}")

class RepoManager:
    """
    Manages the local shallow clone of the OSS-Fuzz repository.
    """

    def __init__(self, repo_url: str = OSS_FUZZ_REPO_URL, sparse_dir: str = "projects", clone_depth: int = CLONE_DEPTH):
        self.repo_url = repo_url
        self.sparse_dir = sparse_dir
        self.clone_depth = clone_depth
        self.clone_path: Path = Path("data/oss-fuzz")
        self._last_checked: Optional[datetime] = None
        self._check_interval = timedelta(minutes=10)
        self.headers = DEFAULT_HEADERS

    def is_up_to_date(self) -> bool:
        """
        Checks whether the local repository is up-to-date with the remote main branch
        """
        if self._last_checked and datetime.now() - self._last_checked < self._check_interval:
            return True

        self._last_checked = datetime.now()

        try:
            local_commit = subprocess.check_output(
                ["git", "-C", str(self.clone_path), "rev-parse", "HEAD"],
                text=True
            ).strip()

            parsed = urlparse(self.repo_url)
            owner_repo = parsed.path.lstrip("/").removesuffix(".git")
            api_url = f"https://api.github.com/repos/{owner_repo}/branches/master"

            remote_data = fetch_from_url(api_url, headers=self.headers, max_retries=1, format="json")
            remote_commit = remote_data["commit"]["sha"]

            return local_commit == remote_commit

        except (FetchError, subprocess.CalledProcessError, KeyError) as e:
            logger.warning(f"Failed to check if repo is up-to-date: {e}")
            return False

    def ensure_repo(self) -> Path:
        """
        Ensures the repo is shallow-cloned and updated locally.
        Falls back to using existing clone if update check or pull fails.
        """
        sparse_path = self.clone_path / self.sparse_dir

        if sparse_path.exists():
            try:
                if not self.is_up_to_date():
                    logger.debug("Updating local clone...")
                    subprocess.run(
                        ["git", "-C", str(self.clone_path), "pull", "--depth", str(self.clone_depth)],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    logger.debug("Repository updated successfully.")
            except Exception as e:
                logger.warning(f"Could not update repo: {e}")
                logger.warning("Proceeding with existing local clone.")
            return sparse_path

        try:
            return shallow_clone_repo(
                repo_url=self.repo_url,
                depth=self.clone_depth,
                sparse_dir=self.sparse_dir
            )
        except Exception as e:
            logger.error(f"Failed to clone OSS-Fuzz repository: {e}")
            raise RuntimeError(f"Failed to clone OSS-Fuzz repository: {e}")

    def get_projects_dir(self) -> Path:
        """
        Returns the path to the local projects directory.
        Clones/updates the repo if needed.
        """
        path = self.ensure_repo()
        if not path.exists():
            raise FileNotFoundError(f"Projects directory not found at {path}")
        return path

_repo_instance = None

def get_repo_manager():
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = RepoManager()
    return _repo_instance