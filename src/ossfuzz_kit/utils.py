import subprocess
import tempfile
from pathlib import Path
from typing import Tuple

# TODO: Make docstring better for this
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