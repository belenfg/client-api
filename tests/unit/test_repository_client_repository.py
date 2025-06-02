import pytest
import json
from pathlib import Path
from repository.client_repository import ClientRepository, RepositoryError


def test_repository_initializes_file(tmp_path):
    """Ensure that initializing the repository creates the JSON file with [] contents."""
    file_path = tmp_path / "clients_test.json"
    repo = ClientRepository(file_path=str(file_path))
    assert file_path.exists()
    content = json.loads(file_path.read_text())
    assert content == []


def test_find_all_returns_list(tmp_path):
    """Repository.find_all() should return a list (initially empty)."""
    file_path = tmp_path / "clients.json"
    repo = ClientRepository(file_path=str(file_path))
    result = repo.find_all()
    assert isinstance(result, list)
    assert result == []


def test_find_all_after_manual_delete(tmp_path):
    """Repository should recreate file when deleted and find_all returns []."""
    file_path = tmp_path / "clients_recreate.json"
    repo = ClientRepository(file_path=str(file_path))
    # Delete file externally
    Path(file_path).unlink()
    # find_all should re-create and return []
    result = repo.find_all()
    assert result == []
    assert file_path.exists()