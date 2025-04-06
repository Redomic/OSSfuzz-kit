import requests
import yaml
import logging
from typing import Any

from ossfuzz_kit.utils import fetch_from_url, get_repo_manager

logger = logging.getLogger("ossfuzz_kit")

def get_project_info(project_name: str, raw: bool = False, use_fallback: bool = True) -> dict[str, Any]:
    """
    Retrieves project metadata from OSS-Fuzz Project's `project.yaml`

    Args:
        project_name: Name of the OSS-Fuzz project.
        raw: If True, return full YAML contents merged with name.

    Returns:
        Dict with structured metadata or raw YAML merged.
    """
    try:
        manager = get_repo_manager()
        projects_dir = manager.get_projects_dir()
        yaml_path = projects_dir / project_name / "project.yaml"

        if not yaml_path.exists():
            raise FileNotFoundError(f"Local file {yaml_path} does not exist")

        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

    except Exception as e:
        logger.warning(f"Failed to load project.yaml from local clone for '{project_name}': {e}")
        url = f"https://raw.githubusercontent.com/google/oss-fuzz/master/projects/{project_name}/project.yaml"
        logger.warning(f"Falling back to fetching project.yaml from remote: {url}")

        try:
            response = fetch_from_url(url, format="text")
            data = yaml.safe_load(response)
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch project.yaml for {project_name}: {e}")
        except yaml.YAMLError as e:
            raise RuntimeError(f"Error parsing YAML for {project_name}: {e}")

    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected YAML format for {project_name}")

    if raw:
        return {
            "name": project_name,
            **data
        }
    else:
        return {
            "name": project_name,
            "language": data.get("language"),
            "build_system": data.get("build"),
            "fuzzing_engines": data.get("fuzzing_engines") or [],
            "sanitizers": data.get("sanitizers") or [],
            "architectures": data.get("architectures") or [],
            "homepage": data.get("homepage"),
            "repo": data.get("main_repo"),
            "primary_contact": data.get("primary_contact"),
            "vendor_ccs": data.get("vendor_ccs"),
        }