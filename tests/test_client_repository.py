import json
import pytest
from pathlib import Path

# Import the class under test and the custom exceptions
from repository.client_repository import ClientRepository
from repository.exceptions import (
    DuplicateClientError,
    ClientNotFoundError,
    RepositoryError,
)
from domain.client import Client


@pytest.fixture
def temp_repo_path(tmp_path):
    """
    Returns a string path to a non‐existent 'clients.json' inside pytest's tmp_path.
    When we instantiate ClientRepository(file_path=...), it should auto‐create the file.
    """
    return str(tmp_path / "clients_test.json")


@pytest.fixture
def repo(temp_repo_path):
    """
    Create a fresh ClientRepository pointing at the temporary JSON file.
    The repository will create the file (initialized to []), so we can test on an empty dataset.
    """
    return ClientRepository(file_path=temp_repo_path)


def test_file_creation_if_not_exists(temp_repo_path):
    """
    GIVEN no file at temp_repo_path
    WHEN we create a ClientRepository on that path
    THEN the file should exist and contain an empty JSON list.
    """
    # Before instantiation, the file must not exist
    assert not Path(temp_repo_path).exists()

    _ = ClientRepository(file_path=temp_repo_path)

    # Now the file should exist
    assert Path(temp_repo_path).exists()

    # Its content should be an empty list (JSON[])
    with open(temp_repo_path, "r", encoding="utf-8") as f:
        content = json.load(f)
    assert content == []


def test_save_and_find_by_id(repo: ClientRepository):
    """
    GIVEN an empty repository
    WHEN we save a Client with id="1"
    THEN find_by_id("1") should return a Client instance with matching fields.
    """
    client = Client(id="1", name="Alice", last_name="Smith", age=30)
    saved = repo.save(client)
    assert isinstance(saved, Client)
    assert saved.id == "1"

    found = repo.find_by_id("1")
    assert isinstance(found, Client)
    assert found.id == "1"
    assert found.name == "Alice"
    assert found.last_name == "Smith"
    assert found.age == 30


def test_duplicate_save_raises_error(repo: ClientRepository):
    """
    GIVEN a repository with one Client id="2"
    WHEN we attempt to save another Client with the same id="2"
    THEN DuplicateClientError is raised.
    """
    client1 = Client(id="2", name="Bob", last_name="Jones", age=25)
    repo.save(client1)

    client_duplicate = Client(id="2", name="Robert", last_name="Jones", age=26)
    with pytest.raises(DuplicateClientError) as excinfo:
        repo.save(client_duplicate)

    assert "Client with ID 2 already exists" in str(excinfo.value)


def test_find_all_returns_list_of_clients(repo: ClientRepository):
    """
    GIVEN multiple clients inserted
    WHEN we call find_all()
    THEN we receive a list of Client objects matching what was saved.
    """
    clients = [
        Client(id="3", name="Carol", last_name="White", age=40),
        Client(id="4", name="Dave", last_name="Brown", age=35),
        Client(id="5", name="Eve", last_name="Black", age=28),
    ]
    for c in clients:
        repo.save(c)

    all_clients = repo.find_all()
    # Ensure it’s a list and length matches
    assert isinstance(all_clients, list)
    assert len(all_clients) == 3

    # Check that each returned element is a Client with the expected IDs
    returned_ids = {client.id for client in all_clients}
    assert returned_ids == {"3", "4", "5"}


def test_update_existing_client(repo: ClientRepository):
    """
    GIVEN a saved client id="10"
    WHEN we modify its fields and call update()
    THEN the repository should overwrite the JSON, and find_by_id returns the updated fields.
    """
    client = Client(id="10", name="Frank", last_name="Green", age=50)
    repo.save(client)

    # Change some fields
    client.name = "Franklin"
    client.age = 51

    updated = repo.update(client)
    assert isinstance(updated, Client)
    assert updated.name == "Franklin"
    assert updated.age == 51

    fetched = repo.find_by_id("10")
    assert fetched.name == "Franklin"
    assert fetched.age == 51


def test_update_nonexistent_raises(repo: ClientRepository):
    """
    GIVEN an empty repository
    WHEN we call update(...) with a Client whose id does not exist
    THEN ClientNotFoundError is raised.
    """
    ghost = Client(id="999", name="Ghost", last_name="User", age=99)
    with pytest.raises(ClientNotFoundError) as excinfo:
        repo.update(ghost)

    assert "Client with ID 999 not found" in str(excinfo.value)


def test_delete_existing_client(repo: ClientRepository):
    """
    GIVEN a saved client id="100"
    WHEN we call delete("100")
    THEN delete returns True and subsequent find_by_id("100") is None.
    """
    client = Client(id="100", name="Hank", last_name="Hill", age=45)
    repo.save(client)

    result = repo.delete("100")
    assert result is True

    # Should no longer exist
    assert repo.find_by_id("100") is None


def test_delete_nonexistent_returns_false(repo: ClientRepository):
    """
    GIVEN an empty repository
    WHEN we call delete("not_there")
    THEN delete returns False (no exception).
    """
    result = repo.delete("not_there")
    assert result is False


def test_read_corrupted_json_raises_repository_error(tmp_path):
    """
    GIVEN a file containing invalid JSON
    WHEN find_all() (or any read) is attempted
    THEN RepositoryError is raised.
    """
    path = tmp_path / "corrupt_clients.json"
    # Write invalid JSON ("{ invalid }")
    path.write_text("{ invalid JSON }", encoding="utf-8")

    repo_corrupt = ClientRepository(file_path=str(path))
    with pytest.raises(RepositoryError) as excinfo:
        _ = repo_corrupt.find_all()

    assert "JSON decode error" in str(excinfo.value)


def test_ensure_file_recreated_when_deleted(tmp_path):
    """
    GIVEN a valid JSON file that is deleted externally
    WHEN find_all() is called again
    THEN the repository recreates the file as an empty list and returns [].
    """
    path = tmp_path / "clients_recreate.json"
    repo_initial = ClientRepository(file_path=str(path))
    assert path.exists()

    # Simulate external deletion
    path.unlink()
    assert not path.exists()

    # Re-instantiate to recreate the file
    repo_after_delete = ClientRepository(file_path=str(path))
    assert path.exists()

    # Delete again and call find_all()
    path.unlink()
    assert not path.exists()

    result = repo_after_delete.find_all()
    assert result == []
    assert path.exists()