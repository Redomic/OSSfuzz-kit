OSS_FUZZ_REPO_URL = "https://github.com/google/oss-fuzz.git"
GITHUB_API_URL = "https://api.github.com/repos/google/oss-fuzz/contents/projects"
GIT_TREE_API_URL = "https://api.github.com/repos/google/oss-fuzz/git/trees/master?recursive=1"

CLONE_DEPTH = 1
DEFAULT_TIMEOUT = 10
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "ossfuzz-kit"
}