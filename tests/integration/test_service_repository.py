import json
import os
import pytest
import sys
# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from dto.client_dto import ClientCreateRequest
from service.client_service import ClientService
from repository.client_repository import ClientRepository, DuplicateClientError, ClientNotFoundError

@pytest.fixture
def temp_repo(tmp_path):
    """
    Provide a ClientRepository pointing to a temporary JSON file.
    """
    repo_file = tmp_path / "clients_service_repo.json"
    return ClientRepository(str(repo_file))

@pytest.fixture
def service(temp_repo):
    """
    Provide a ClientService that uses the given temporary repository.
    """
    return ClientService(repository=temp_repo)

def test_create_client_and_persist(service, temp_repo):
    """
    Service.create_client(...) should save a new client with a generated UUID,
    and the repository should contain exactly that client.
    """
    # Construct a ClientCreateRequest DTO to pass to the service
    from dto.client_dto import ClientCreateRequest
    request = ClientCreateRequest(name="Eve", last_name="Adams", age=29)
    client = service.create_client(request)
    assert client.id is not None

    # Check repository content on disk
    with open(temp_repo.file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert len(data) == 1
    assert data[0]["name"] == "Eve"
    assert data[0]["last_name"] == "Adams"
    assert data[0]["age"] == 29

def test_get_client_by_id_success(service, temp_repo):
    """
    After creating a client, get_client_by_id should retrieve the same object.
    """
    # Construct a ClientCreateRequest DTO to pass to the service
    request = ClientCreateRequest(name="Frank", last_name="Miller", age=40)
    created = service.create_client(request)
    fetched = service.get_client_by_id(created.id)
    assert fetched.id == created.id
    assert fetched.name == "Frank"


def test_get_client_by_id_not_found_raises(service):
    """
    Requesting a non-existent client should raise ValueError.
    """
    with pytest.raises(ValueError) as exc_info:
        service.get_client_by_id("nonexistent")
    assert "Client with ID nonexistent not found" in str(exc_info.value)


def test_update_client_success(service, temp_repo):
    """
    After creating a client, updating its fields should persist changes.
    """
    # Construct a ClientCreateRequest DTO to create initial client
    from dto.client_dto import ClientCreateRequest, ClientUpdateRequest
    create_request = ClientCreateRequest(name="Grace", last_name="Hopper", age=85)
    created = service.create_client(create_request)

    # Now construct a ClientUpdateRequest DTO for the update
    update_request = ClientUpdateRequest(name=None, last_name=None, age=86)
    updated = service.update_client(created.id, update_request)
    assert updated.age == 86

    # Confirm on disk
    with open(temp_repo.file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data[0]["age"] == 86

    # Ensure other fields remain unchanged
    assert data[0]["name"] == "Grace"
    assert data[0]["last_name"] == "Hopper"

def test_update_client_not_found_raises(service):
    """
    Attempting to update a non-existent client should raise ValueError.
    """
    from dto.client_dto import ClientUpdateRequest
    update_request = ClientUpdateRequest(name="X", last_name="Y", age=50)
    with pytest.raises(ValueError) as exc_info:
        service.update_client("x-ray", update_request)
    assert "Client with ID x-ray not found" in str(exc_info.value)

def test_delete_client_success(service, temp_repo):
    """
    Deleting an existing client should remove it from the repository.
    """
    from dto.client_dto import ClientCreateRequest
    request = ClientCreateRequest(name="Helen", last_name="Smith", age=50)
    created = service.create_client(request)
    result = service.delete_client(created.id)
    assert result is True

    # Confirm repository is empty on disk
    with open(temp_repo.file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data == []

def test_delete_client_not_found_raises(service):
    """
    Deleting a non-existent client should raise ValueError.
    """
    with pytest.raises(ValueError) as exc_info:
        service.delete_client("zulu")
    assert "Client with ID zulu not found" in str(exc_info.value)

def test_get_all_clients_returns_all(service, temp_repo):
    """
    get_all_clients should return a list of all clients in the repository.
    """
    from dto.client_dto import ClientCreateRequest
    c1_request = ClientCreateRequest(name="Ian", last_name="Fleming", age=56)
    c2_request = ClientCreateRequest(name="Jack", last_name="Ryan", age=60)
    c1 = service.create_client(c1_request)
    c2 = service.create_client(c2_request)
    all_clients = service.get_all_clients()
    ids = [c.id for c in all_clients]
    assert c1.id in ids and c2.id in ids
