from ossfuzz_kit.client import OSSFuzzClient

def handle_list_projects(args):
    """Handles 'list-projects' CLI command"""
    client = OSSFuzzClient()
    projects = client.get_all_projects()

    limit = args.limit if args.limit is not None else len(projects)
    
    for project in projects[:limit]:
        print(project)

    print(f"\nTotal projects listed: {min(limit, len(projects))} / {len(projects)}")

def handle_project_details(args):
    """Handles 'project-details' CLI command."""
    client = OSSFuzzClient()
    
    try:
        project_info = client.get_project_details(args.project, raw=args.raw)

        print(f"Details for project: {args.project}\n")
        for key, value in project_info.items():
            print(f"{key}: {value}")

    except Exception as e:
        print(f"[Error] Failed to retrieve project details: {e}")