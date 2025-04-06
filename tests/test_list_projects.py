import pytest
from unittest import mock

from ossfuzz_kit.project_info.list_projects import list_all_projects

@pytest.fixture
def mock_projects_dir(tmp_path):
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    (projects_dir / "proj1").mkdir()
    (projects_dir / "proj2").mkdir()
    return projects_dir

@mock.patch("ossfuzz_kit.project_info.list_projects.get_repo_manager")
def test_list_projects_local_success(mock_get_repo_manager, mock_projects_dir):
    mock_manager = mock.Mock()
    mock_manager.get_projects_dir.return_value = mock_projects_dir
    mock_get_repo_manager.return_value = mock_manager

    result = list_all_projects(use_fallback=False)
    assert sorted(result) == ["proj1", "proj2"]

@mock.patch("ossfuzz_kit.project_info.list_projects.fetch_from_url")
@mock.patch("ossfuzz_kit.project_info.list_projects.get_repo_manager")
def test_list_projects_fallback_success(mock_get_repo_manager, mock_fetch_from_url):
    mock_manager = mock.Mock()
    mock_manager.get_projects_dir.side_effect = FileNotFoundError("Local clone not available")
    mock_get_repo_manager.return_value = mock_manager

    mock_fetch_from_url.return_value = {
        "tree": [
            {"path": "projects/projA", "type": "tree"},
            {"path": "projects/projB", "type": "tree"},
        ]
    }

    result = list_all_projects(use_fallback=True)
    assert sorted(result) == ["projA", "projB"]

@mock.patch("ossfuzz_kit.project_info.list_projects.get_repo_manager")
def test_list_projects_local_failure_no_fallback(mock_get_repo_manager):
    mock_manager = mock.Mock()
    mock_manager.get_projects_dir.side_effect = Exception("something bad happened")
    mock_get_repo_manager.return_value = mock_manager

    with pytest.raises(RuntimeError):
        list_all_projects(use_fallback=False)