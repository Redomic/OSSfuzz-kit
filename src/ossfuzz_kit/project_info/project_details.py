import requests
import yaml

from typing import Any

from ossfuzz_kit.utils import fetch_from_url

def get_project_info(project_name: str, raw: bool = False) -> dict[str, Any]:
    """
    Retrieves project metadata from OSS-Fuzz Project's `project.yaml`

    Args:
        project_name: Name of the OSS-Fuzz project.
        raw: If True, return full YAML contents merged with name.

    Returns:
        Dict with structured metadata or raw YAML merged.
    """

    url = f"https://raw.githubusercontent.com/google/oss-fuzz/master/projects/{project_name}/project.yaml"

    try:
        response = fetch_from_url(url, format="text")
        data = yaml.safe_load(response)

    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch project.yaml for {project_name}, more than likely does not exist: {e}")
    
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