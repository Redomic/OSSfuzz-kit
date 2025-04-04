from ossfuzz_kit.project_info.list_projects import list_all_projects

class OSSFuzzClient:
    def __init__(self):
        # TODO: Expand for caching, config overrides, etc
        pass

    def get_all_projects(self) -> list[str]:
        return list_all_projects()