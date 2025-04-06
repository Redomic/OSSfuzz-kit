# OSSfuzz-kit

`ossfuzz-kit` is a Python library and CLI tool for programmatically interacting with the [OSS-Fuzz](https://github.com/google/oss-fuzz) project infrastructure.

It provides a high-level, user-friendly interface to:

- Query and filter OSS-Fuzz project metadata (language, repo, build system, fuzzing engines)
- Access historical fuzzing results, coverage reports, and crash statistics
- Run custom fuzzing experiments on existing OSS-Fuzz projects
- Export structured data for integration with research or CI pipelines, dashboards, or automation scripts

This toolkit is built for researchers, automation engineers, and security analysts — anyone who wants to explore or extend OSS-Fuzz’s capabilities without diving into its full infrastructure.

> Developed as part of a GSoC 2025 initiative to build a self-contained, research-oriented OSS-Fuzz interface with modular design and full local reproducibility.

---

## Installation

**Requirements**: Python 3.8+ and Git

### From [TestPyPI](https://test.pypi.org/project/ossfuzz-kit/)

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple ossfuzz-kit
```

### From source (for development)

```bash
git clone https://github.com/YOUR_USERNAME/ossfuzz-kit.git
cd ossfuzz-kit
poetry install
```

---

## Sample Usage

Extensive Docs coming soon

### Python

```python
from ossfuzz_kit.client import OSSFuzzClient

client = OSSFuzzClient()

# Get all project names
projects = client.get_all_projects()
print(len(projects), "projects found.")

# Get info about a specific project
info = client.get_project_details("curl")
print(info["language"], info["repo"], info["fuzzing_engines"])
```

### CLI

#### List all projects

```bash
ossfuzz-kit list-projects

# With a limit
ossfuzz-kit list-projects --limit 50
```

#### Get project details

```bash
ossfuzz-kit project-details zlib

# If you want the raw file
ossfuzz-kit project-details zlib --raw

# disable fallback to API, only use shallow copy
ossfuzz-kit --no-fallback project-details zlib
```

---

## Testing

```bash
poetry run pytest tests/
```

All tests run locally and don’t require hitting the GitHub API unless explicitly configured to do so.

---
## Roadmap

This project will exponentially grow over time. Here's what's coming:

### ✅ Project Info
- [x] List all OSS-Fuzz projects
- [x] Fetch project metadata (language, build system, repo)
- [ ] Filter projects by language/library

### 📜 Fuzzing Results (WIP)
- [ ] Coverage data by date/project
- [ ] Crash reports + stats
- [ ] Date range filtering
- [ ] Structured JSON output

### ⚙️ Custom Fuzzing (Future)
- [ ] Define + run custom fuzz targets
- [ ] Monitor run status
- [ ] Pull down coverage/crashes/results

### 🧱 Design Goals
- [ ] Modular structure
- [x] pip-installable
- [ ] Docs + examples in progress
- [ ] CLI + Python API supported

---

## Contributing

Ideas, feedback, and issues are welcome.

Right now, we’re not accepting PRs — CI/CD is still being set up. Once that’s ready, contributions will open up fully.

---

## License

Apache 2.0 © 2025
