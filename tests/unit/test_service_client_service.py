import pytest
from service.client_service import ClientService
from domain.client import Client


class DummyRepo:
    def __init__(self):
        self.storage = []

    def find_all(self):
        return self.storage

    def save(self, client: Client):
        self.storage.append(client)
        return client


@pytest.fixture
def dummy_repo():
    return DummyRepo()


@pytest.fixture
def service(dummy_repo):
    return ClientService(repository=dummy_repo)


def test_service_add_client(service):
    """Service should add a new client via repository, preserving its fields."""
    client = Client(id="1", name="Alice", last_name="Wonderland", age=30)
    result = service.create_client(client)

    assert isinstance(result, Client)

    assert result.name == client.name
    assert result.last_name == client.last_name
    assert result.age == client.age

    stored = service.repository.find_all()
    assert len(stored) == 1

    stored_client = stored[0]
    assert stored_client.name == client.name
    assert stored_client.last_name == client.last_name
    assert stored_client.age == client.age


def test_service_get_all_clients_empty(service):
    """Service.get_all should return empty list initially."""
    result = service.get_all_clients()
    assert isinstance(result, list)
    assert result == []
