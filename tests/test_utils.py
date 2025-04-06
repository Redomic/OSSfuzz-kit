import pytest
import requests
from unittest.mock import patch, MagicMock
from ossfuzz_kit.utils import (
    fetch_from_url,
    shallow_clone_repo,
    RepoManager,
    FetchError
)
from pathlib import Path


@patch("ossfuzz_kit.utils.requests.get")
def test_fetch_from_url_text_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "Success"

    result = fetch_from_url("http://example.com")
    assert result == "Success"


@patch("ossfuzz_kit.utils.requests.get")
def test_fetch_from_url_json_success(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"ok": True}

    result = fetch_from_url("http://example.com", format="json")
    assert result == {"ok": True}


@patch("ossfuzz_kit.utils.requests.get")
def test_fetch_from_url_retry_failure(mock_get):
    mock_get.side_effect = requests.RequestException("Network down")

    with pytest.raises(FetchError):
        fetch_from_url("http://example.com", max_retries=2)


@patch("ossfuzz_kit.utils.subprocess.run")
@patch("ossfuzz_kit.utils.Path.exists", return_value=False)
def test_shallow_clone_repo_success(mock_exists, mock_run):
    with patch("ossfuzz_kit.utils.tqdm") as mock_tqdm:
        path = shallow_clone_repo("https://github.com/example/repo.git")
        assert "oss-fuzz" in str(path)


@patch("ossfuzz_kit.utils.subprocess.run")
@patch("ossfuzz_kit.utils.fetch_from_url")
@patch("ossfuzz_kit.utils.subprocess.check_output")
def test_repo_manager_is_up_to_date_true(mock_check_output, mock_fetch, mock_run):
    mock_check_output.return_value = "abc123"
    mock_fetch.return_value = {"commit": {"sha": "abc123"}}

    manager = RepoManager()
    assert manager.is_up_to_date() is True


@patch("ossfuzz_kit.utils.RepoManager.is_up_to_date", return_value=False)
@patch("ossfuzz_kit.utils.subprocess.run")
@patch("ossfuzz_kit.utils.Path.exists", return_value=True)
def test_repo_manager_ensure_repo_updates(mock_exists, mock_run, mock_is_up_to_date):
    manager = RepoManager()
    path = manager.ensure_repo()
    assert "oss-fuzz" in str(path)


@patch("ossfuzz_kit.utils.RepoManager.ensure_repo")
@patch("ossfuzz_kit.utils.Path.exists", return_value=True)
def test_get_projects_dir_success(mock_exists, mock_ensure_repo):
    mock_ensure_repo.return_value = Path("data/oss-fuzz/projects")
    manager = RepoManager()
    assert manager.get_projects_dir() == Path("data/oss-fuzz/projects")