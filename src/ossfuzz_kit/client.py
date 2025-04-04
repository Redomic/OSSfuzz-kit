from ossfuzz_kit.project_info.list_projects import list_all_projects
from ossfuzz_kit.project_info.project_details import get_project_info

class OSSFuzzClient:
    def __init__(self):
        # TODO: Expand for caching, config overrides, etc
        pass

    def get_all_projects(self) -> list[str]:
        """
        Returns a list of all OSS-Fuzz projects.
        """
        return list_all_projects()
    
    def get_project_details(self, project_name: str, raw: bool = False) -> dict:
        """
        Fetch metadata for a specific OSS-Fuzz project.
        """
        return get_project_info(project_name=project_name, raw=raw)