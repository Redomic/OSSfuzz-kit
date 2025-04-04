import subprocess
import tempfile
import time
from pathlib import Path
from typing import Tuple

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

def shallow_clone_repo(repo_url: str, depth: int = 1) -> Tuple[Path, tempfile.TemporaryDirectory]:
    """
    Shallow clones a git repository and returns the path to the clone and the TemporaryDirectory object.
    """
    tmpdir = tempfile.TemporaryDirectory()

    try:
        subprocess.run(
            ["git", "clone", "--depth", str(depth), repo_url, tmpdir.name],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    except subprocess.CalledProcessError as e:
        tmpdir.cleanup()
        raise RuntimeError(f"Git clone failed: {e}")
    
    return Path(tmpdir.name), tmpdir