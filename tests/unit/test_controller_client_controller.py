import pytest
from fastapi.testclient import TestClient
from fastapi import status
from typing import List

# Import the FastAPI app and the dependency to override
from main import app
from controller.client_controller import get_client_service
from domain.client import Client
from dto.client_dto import ClientCreateRequest, ClientUpdateRequest


# Helper to create a deterministic Client instance for testing
def create_test_client(
    id: str = "test-id",
    name: str = "Alice",
    last_name: str = "Smith",
    age: int = 30,
    created_at: str = "2025-01-01T00:00:00"
) -> Client:
    """
    Create a Client domain object with fixed timestamp for predictable responses.
    """
    client = Client(id=id, name=name, last_name=last_name, age=age)
    client.created_at = created_at
    return client


class FakeService:
    """
    A fake ClientService that can be configured to return predetermined values
    or raise exceptions to simulate various scenarios in controller tests.
    """

    def __init__(self):
        # Attributes to configure behavior in each test
        self.clients: List[Client] = []
        self.raise_on_get_all = None
        self.raise_on_get_by_id = {}
        self.raise_on_create = None
        self.raise_on_update = {}
        self.raise_on_delete = {}

    def get_all_clients(self) -> List[Client]:
        if self.raise_on_get_all:
            raise self.raise_on_get_all
        return self.clients

    def get_client_by_id(self, client_id: str) -> Client:
        if client_id in self.raise_on_get_by_id:
            raise self.raise_on_get_by_id[client_id]
        for c in self.clients:
            if c.id == client_id:
                return c
        # If not explicitly configured to raise, mimic service behavior
        raise ValueError(f"Client with ID {client_id} not found")

    def create_client(self, request: ClientCreateRequest) -> Client:
        if self.raise_on_create:
            raise self.raise_on_create
        # Return a new Client using data from the request
        new_client = create_test_client(
            id="new-id",
            name=request.name,
            last_name=request.last_name,
            age=request.age
        )
        return new_client

    def update_client(self, client_id: str, request: ClientUpdateRequest) -> Client:
        if client_id in self.raise_on_update:
            raise self.raise_on_update[client_id]
        for c in self.clients:
            if c.id == client_id:
                # Simulate in-place update as real service would
                if request.name is not None:
                    c.name = request.name
                if request.last_name is not None:
                    c.last_name = request.last_name
                if request.age is not None:
                    c.age = request.age
                return c
        raise ValueError(f"Client with ID {client_id} not found")

    def delete_client(self, client_id: str) -> None:
        if client_id in self.raise_on_delete:
            raise self.raise_on_delete[client_id]
        for idx, c in enumerate(self.clients):
            if c.id == client_id:
                del self.clients[idx]
                return
        raise ValueError(f"Client with ID {client_id} not found")


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    """
    Clear any existing dependency overrides before and after each test.
    """
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


@pytest.fixture
def client():
    """
    Provide a TestClient instance for the FastAPI app.
    """
    return TestClient(app)


def override_service(fake_service: FakeService):
    """
    Shortcut to override the get_client_service dependency with our fake.
    """
    app.dependency_overrides[get_client_service] = lambda: fake_service


class TestGetAllClients:
    """
    Tests for the GET /clients endpoint.
    """

    def test_get_all_clients_success(self, client):
        """
        When the service returns a list of clients, the endpoint should return HTTP 200
        and a JSON list with correct fields.
        """
        fake = FakeService()
        # Prepopulate fake service with two clients
        fake.clients = [
            create_test_client(id="id1", name="Alice", last_name="Smith", age=30),
            create_test_client(id="id2", name="Bob", last_name="Johnson", age=45),
        ]
        override_service(fake)

        response = client.get("/clients")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        # Expect a list of two items
        assert isinstance(data, list)
        assert len(data) == 2

        # Verify the first item’s structure
        client1 = data[0]
        assert client1["id"] == "id1"
        assert client1["name"] == "Alice"
        assert client1["last_name"] == "Smith"
        assert client1["age"] == 30
        assert client1["created_at"] == "2025-01-01T00:00:00"

    def test_get_all_clients_server_error(self, client):
        """
        Simulate a generic exception in service.get_all_clients, expect HTTP 500.
        """
        fake = FakeService()
        fake.raise_on_get_all = RuntimeError("Unexpected service failure")
        override_service(fake)

        response = client.get("/clients")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Unexpected service failure" in response.json()["detail"]


class TestGetClientById:
    """
    Tests for the GET /clients/{client_id} endpoint.
    """

    def test_get_client_by_id_success(self, client):
        """
        When the service returns a client, expect HTTP 200 and correct JSON.
        """
        fake = FakeService()
        fake.clients = [create_test_client(id="id1", name="Carol", last_name="King", age=28)]
        override_service(fake)

        response = client.get("/clients/id1")
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == "id1"
        assert data["name"] == "Carol"
        assert data["last_name"] == "King"
        assert data["age"] == 28
        assert data["created_at"] == "2025-01-01T00:00:00"

    def test_get_client_by_id_not_found(self, client):
        """
        If service.get_client_by_id raises ValueError, expect HTTP 404.
        """
        fake = FakeService()
        fake.clients = []  # No clients present
        # Configure the fake to raise ValueError for this ID
        fake.raise_on_get_by_id["unknown-id"] = ValueError("Client with ID unknown-id not found")
        override_service(fake)

        response = client.get("/clients/unknown-id")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Client with ID unknown-id not found" in response.json()["detail"]

    def test_get_client_by_id_server_error(self, client):
        """
        Simulate a generic exception in service.get_client_by_id, expect HTTP 500.
        """
        fake = FakeService()
        fake.raise_on_get_by_id["id1"] = RuntimeError("Database unreachable")
        override_service(fake)

        response = client.get("/clients/id1")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database unreachable" in response.json()["detail"]


class TestCreateClient:
    """
    Tests for the POST /clients endpoint.
    """

    def test_create_client_success(self, client):
        """
        Sending valid payload should result in HTTP 201 with created client fields.
        """
        fake = FakeService()
        override_service(fake)

        payload = {"name": "Diana", "last_name": "Prince", "age": 32}
        response = client.post("/clients", json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        data = response.json()
        assert data["id"] == "new-id"
        assert data["name"] == "Diana"
        assert data["last_name"] == "Prince"
        assert data["age"] == 32
        # created_at should match our helper’s default
        assert data["created_at"] == "2025-01-01T00:00:00"

    def test_create_client_validation_error(self, client):
        """
        Sending invalid payload (e.g., missing required fields or invalid age)
        should result in HTTP 422 from FastAPI/Pydantic.
        """
        fake = FakeService()
        override_service(fake)

        # Missing "name" field
        payload_missing = {"last_name": "Wayne", "age": 27}
        response1 = client.post("/clients", json=payload_missing)
        assert response1.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

        # Invalid age (negative)
        payload_invalid = {"name": "Bruce", "last_name": "Wayne", "age": -5}
        response2 = client.post("/clients", json=payload_invalid)
        assert response2.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_client_server_error(self, client):
        """
        If service.create_client raises a generic exception, expect HTTP 500.
        """
        fake = FakeService()
        fake.raise_on_create = RuntimeError("Service failed to create")
        override_service(fake)

        payload = {"name": "Eve", "last_name": "Adams", "age": 29}
        response = client.post("/clients", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Service failed to create" in response.json()["detail"]


class TestUpdateClient:
    """
    Tests for the PUT /clients/{client_id} endpoint.
    """

    def test_update_client_success(self, client):
        """
        For an existing client, a valid update payload should return HTTP 200
        and the updated client data.
        """
        fake = FakeService()
        # Prepopulate with a client whose age we will update
        initial = create_test_client(id="id42", name="Frank", last_name="Miller", age=40)
        fake.clients = [initial]
        override_service(fake)

        payload = {"age": 41}
        response = client.put("/clients/id42", json=payload)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert data["id"] == "id42"
        assert data["name"] == "Frank"
        assert data["last_name"] == "Miller"
        assert data["age"] == 41
        assert data["created_at"] == "2025-01-01T00:00:00"

    def test_update_client_not_found(self, client):
        """
        If the client does not exist, service.update_client should raise ValueError,
        leading to HTTP 404 at the controller.
        """
        fake = FakeService()
        # No clients in fake
        fake.raise_on_update["missing-id"] = ValueError("Client with ID missing-id not found")
        override_service(fake)

        payload = {"name": "George"}
        response = client.put("/clients/missing-id", json=payload)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Client with ID missing-id not found" in response.json()["detail"]

    def test_update_client_validation_error(self, client):
        """
        Sending invalid data (e.g., age out of range) should trigger HTTP 422.
        """
        fake = FakeService()
        # Prepopulate a client so that validation occurs first
        fake.clients = [create_test_client(id="id43", name="Helen", last_name="Smith", age=50)]
        override_service(fake)

        # Invalid update: age is greater than 150
        payload = {"age": 200}
        response = client.put("/clients/id43", json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_update_client_server_error(self, client):
        """
        If service.update_client raises a generic exception, expect HTTP 500.
        """
        fake = FakeService()
        fake.raise_on_update["id44"] = RuntimeError("Database locked")
        override_service(fake)

        payload = {"last_name": "Johnson"}
        response = client.put("/clients/id44", json=payload)
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Database locked" in response.json()["detail"]


class TestDeleteClient:
    """
    Tests for the DELETE /clients/{client_id} endpoint.
    """

    def test_delete_client_success(self, client):
        """
        When the client exists, service.delete_client should succeed,
        and the endpoint returns HTTP 204 with no content.
        """
        fake = FakeService()
        # Prepopulate with a client to be deleted
        fake.clients = [create_test_client(id="del-id", name="Ivan", last_name="Petrov", age=38)]
        override_service(fake)

        response = client.delete("/clients/del-id")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        # Body should be empty
        assert response.content == b""

    def test_delete_client_not_found(self, client):
        """
        If the client does not exist, service.delete_client raises ValueError,
        leading to HTTP 404.
        """
        fake = FakeService()
        fake.raise_on_delete["nope"] = ValueError("Client with ID nope not found")
        override_service(fake)

        response = client.delete("/clients/nope")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Client with ID nope not found" in response.json()["detail"]

    def test_delete_client_server_error(self, client):
        """
        If service.delete_client raises a generic exception, expect HTTP 500.
        """
        fake = FakeService()
        fake.raise_on_delete["err-id"] = RuntimeError("Internal cleanup failure")
        override_service(fake)

        response = client.delete("/clients/err-id")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "Internal cleanup failure" in response.json()["detail"]
