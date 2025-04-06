import pytest
from unittest.mock import patch, mock_open, MagicMock
from ossfuzz_kit.project_info.project_details import get_project_info

def test_get_project_info_local_success():
    fake_yaml = """
    language: c++
    build: cmake
    fuzzing_engines:
      - libfuzzer
    sanitizers:
      - address
    architectures:
      - x86_64
    homepage: https://example.com
    main_repo: https://github.com/example/project
    primary_contact: contact@example.com
    vendor_ccs: ["vendor@example.com"]
    """

    with patch("ossfuzz_kit.project_info.project_details.get_repo_manager") as mock_manager:
        mock_projects_dir = MagicMock()
        yaml_path = mock_projects_dir.__truediv__.return_value
        yaml_path.exists.return_value = True

        mock_manager.return_value.get_projects_dir.return_value = mock_projects_dir

        with patch("builtins.open", mock_open(read_data=fake_yaml)):
            result = get_project_info("fake-project")

    assert result["name"] == "fake-project"
    assert result["language"] == "c++"
    assert "fuzzing_engines" in result

def test_get_project_info_no_fallback_raises():
    with patch("ossfuzz_kit.project_info.project_details.get_repo_manager") as mock_manager:
        mock_projects_dir = MagicMock()
        yaml_path = mock_projects_dir.__truediv__.return_value
        yaml_path.exists.return_value = False

        mock_manager.return_value.get_projects_dir.return_value = mock_projects_dir

        with pytest.raises(RuntimeError):
            get_project_info("fail-project", use_fallback=False)