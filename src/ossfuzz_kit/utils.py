import subprocess
import tempfile
import time
import sys
from tqdm import tqdm
from pathlib import Path

import requests
from requests.exceptions import RequestException

from ossfuzz_kit.config import DEFAULT_TIMEOUT, DEFAULT_HEADERS

class FetchError(Exception):
    """Raised when a URL fetch fails."""
    pass

def fetch_from_url(
    url: str,
    headers: dict = None,
    timeout: int = DEFAULT_TIMEOUT,
    max_retries: int = 3,
    format: str = "text"
) -> str:
    """
    Fetches raw text content from a URL with retries and exponential backoff.

    Args:
        url: URL to fetch.
        headers: Optional HTTP headers.
        timeout: Timeout per request in seconds.
        max_retries: Max number of retries on failure.
        format: Return format — "text", "json", or "bytes".

    Returns:
        str: Response text if successful.
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
            print(f"[Retry {attempt}] Failed to fetch {url}. Retrying in {wait_time:.1f}s...")
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
        print(f"Cloning {repo_url} (sparse: '{sparse_dir}')...\n")

        with tqdm(total=2, desc="Cloning repo", unit="step", file=sys.stdout) as pbar:
            subprocess.run(
                [
                    "git", 
                    "clone", 
                    "--depth", str(depth), 
                    "--filter=blob:none", 
                    "--sparse", 
                    repo_url, 
                    str(clone_path)
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pbar.update(1)

            subprocess.run(
                [
                    "git", 
                    "-C", str(clone_path), 
                    "sparse-checkout", 
                    "set", sparse_dir
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            pbar.update(1)

        return clone_path / sparse_dir

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Git clone failed: {e}")