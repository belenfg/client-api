import json
import os
import pytest
import sys
# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from repository.client_repository import ClientRepository, RepositoryError, DuplicateClientError, ClientNotFoundError
from domain.client import Client

@pytest.fixture
def temp_repo_file(tmp_path):
    """
    Provide a path to a temporary JSON file for the repository.
    """
    repo_file = tmp_path / "clients_repo_fs.json"
    return str(repo_file)

def test_initialize_creates_empty_json(temp_repo_file):
    """
    When initializing ClientRepository with a non-existent file path,
    the repository should create the file with an empty JSON array.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    # The file should exist now
    assert os.path.exists(temp_repo_file)
    # And its content should be an empty list
    with open(temp_repo_file, "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content == "[]"

def test_find_all_on_empty_returns_empty_list(temp_repo_file):
    """
    Calling find_all() on an empty repository should return an empty list.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    all_clients = repo.find_all()
    assert isinstance(all_clients, list)
    assert all_clients == []

def test_save_and_find_by_id_persists_client(temp_repo_file):
    """
    After saving a Client to the repository, find_by_id should retrieve it,
    and the JSON file should contain its data.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    client = Client(id="c1", name="Test", last_name="User", age=25)
    repo.save(client)

    # find_by_id should return a Client with matching attributes
    fetched = repo.find_by_id("c1")
    assert fetched is not None
    assert fetched.id == "c1"
    assert fetched.name == "Test"
    assert fetched.last_name == "User"
    assert fetched.age == 25

    # The JSON file should contain exactly one JSON object with id "c1"
    with open(temp_repo_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == "c1"

def test_duplicate_client_error_on_save(temp_repo_file):
    """
    Saving two Clients with the same ID should raise DuplicateClientError.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    client1 = Client(id="dup", name="A", last_name="B", age=20)
    client2 = Client(id="dup", name="C", last_name="D", age=30)
    repo.save(client1)
    with pytest.raises(DuplicateClientError):
        repo.save(client2)

def test_update_nonexistent_client_raises_error(temp_repo_file):
    """
    Calling update() on a non-existent client should raise ClientNotFoundError.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    client = Client(id="x", name="X", last_name="Y", age=40)
    with pytest.raises(ClientNotFoundError):
        repo.update(client)

def test_delete_nonexistent_client_returns_false(temp_repo_file):
    """
    Deleting a client ID that does not exist should return False and not create file errors.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    result = repo.delete("no-id")
    assert result is False

def test_delete_existing_client_removes_from_file(temp_repo_file):
    """
    Deleting a valid client should return True and remove it from the JSON file.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    client = Client(id="to-delete", name="Del", last_name="Client", age=50)
    repo.save(client)

    result = repo.delete("to-delete")
    assert result is True

    # JSON file should now be an empty list
    with open(temp_repo_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == []

def test_find_all_with_multiple_clients_preserves_order(temp_repo_file):
    """
    Saving multiple clients and calling find_all() should return them in saved order.
    """
    repo = ClientRepository(file_path=temp_repo_file)
    client_a = Client(id="a", name="A", last_name="Alpha", age=30)
    client_b = Client(id="b", name="B", last_name="Beta", age=31)
    repo.save(client_a)
    repo.save(client_b)

    all_clients = repo.find_all()
    assert [c.id for c in all_clients] == ["a", "b"]

def test_malformed_json_raises_repository_error(tmp_path):
    """
    If the JSON file content is corrupted, find_all() should raise RepositoryError.
    """
    file_path = tmp_path / "malformed.json"
    # Write invalid JSON
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("INVALID_JSON")
    repo = ClientRepository(file_path=str(file_path))
    with pytest.raises(RepositoryError):
        repo.find_all()
