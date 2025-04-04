import json
import functools
import sys
from ossfuzz_kit.client import OSSFuzzClient

client = OSSFuzzClient()

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def cli_handler(func):
    """Decorator to wrap CLI commands with error handling."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"{RED}Command failed:{RESET} {e}")
            sys.exit(1)
    return wrapper

@cli_handler
def handle_list_projects(args):
    """Handles 'list-projects' CLI commands"""

    print(f"{CYAN}Fetching OSS-Fuzz projects...{RESET}")
    projects = client.get_all_projects()
    limit = args.limit if args.limit is not None else len(projects)
        
    for project in projects[:limit]:
        print(project)

    print(f"\n{BOLD}{GREEN}Total projects listed: {min(limit, len(projects))} / {len(projects)}{RESET}")

@cli_handler
def handle_project_details(args):
    """Handles 'project-details' CLI commands"""

    print(f"{CYAN}Fetching details for project: {args.project}{RESET}")
    details = client.get_project_details(args.project, raw=args.raw)
    formatted = json.dumps(details, indent=2, sort_keys=False)
    print(formatted)