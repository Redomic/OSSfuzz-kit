from ossfuzz_kit.client import OSSFuzzClient

def handle_list_projects(args):
    """Handles 'list-projects' CLI command"""
    client = OSSFuzzClient()
    projects = client.get_all_projects()

    limit = args.limit if args.limit is not None else len(projects)
    
    for project in projects[:limit]:
        print(project)

    print(f"\nTotal projects listed: {min(limit, len(projects))} / {len(projects)}")