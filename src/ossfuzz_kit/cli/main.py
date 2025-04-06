import argparse
import sys
import logging

from importlib.metadata import version, PackageNotFoundError

from src.ossfuzz_kit.cli.commands.project_info import handle_list_projects, handle_project_details

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ossfuzz-kit")

def get_package_version(pkg_name: str = "ossfuzz-kit") -> str:
    try:
        return version(pkg_name)
    except PackageNotFoundError:
        return "unknown"

def get_parser():
    parser = argparse.ArgumentParser(
        description="OSSFuzz-Kit CLI — Interact with OSS-Fuzz"
    )
    parser.add_argument('--version', action='version', version=f'ossfuzz-kit {get_package_version()}')
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Disable the Github API as fallback"
    )

    subparsers = parser.add_subparsers(dest="command", title="Commands", required=True)

    # --- list-projects ---
    list_cmd = subparsers.add_parser("list-projects", help="List all OSS-Fuzz projects")
    list_cmd.add_argument("--limit", type=int, default=None, help="Limit number of projects (default: all)")
    list_cmd.set_defaults(func=handle_list_projects)

    # --- project-details ---
    details_cmd = subparsers.add_parser("project-details", help="Get detailed info for a project")
    details_cmd.add_argument("project", help="Name of the OSS-Fuzz project")
    details_cmd.add_argument("--raw", action="store_true", help="Return full raw metadata from project.yaml")
    details_cmd.set_defaults(func=handle_project_details)

    return parser

def main():
    parser = get_parser()
    args = parser.parse_args()

    try:
        args.func(args)
    except Exception as e:
        logger.error(f"Command failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()