import os
import sys
import json
import pytest

# Add project root to sys.path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi.testclient import TestClient
from fastapi import status

from main import app
from repository.client_repository import ClientRepository
from controller.client_controller import get_client_repository

@pytest.fixture(autouse=True)
def override_repo(tmp_path):
    """
    Override the repository dependency to use a temporary JSON file.
    """
    app.dependency_overrides = {}
    temp_file = tmp_path / "clients_int_controller.json"
    repo = ClientRepository(str(temp_file))
    app.dependency_overrides[get_client_repository] = lambda: repo
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client():
    """
    Provide a TestClient instance for the FastAPI app.
    """
    return TestClient(app)

def test_create_and_read_flow_integration(client, tmp_path):
    """
    Test the integration from controller -> service -> repository -> filesystem.
    """
    # Create a client via POST
    resp = client.post("/clients", json={"name": "Laura", "last_name": "Croft", "age": 33})
    assert resp.status_code == status.HTTP_201_CREATED
    data = resp.json()
    client_id = data["id"]

    # Confirm JSON file on disk has that client
    json_path = tmp_path / "clients_int_controller.json"
    with open(json_path, "r", encoding="utf-8") as f:
        file_data = json.load(f)
    assert len(file_data) == 1
    assert file_data[0]["id"] == client_id

    # Retrieve by ID via GET
    resp_get = client.get(f"/clients/{client_id}")
    assert resp_get.status_code == status.HTTP_200_OK
    get_data = resp_get.json()
    assert get_data["name"] == "Laura"

    # Update via PUT
    resp_put = client.put(f"/clients/{client_id}", json={"age": 34})
    assert resp_put.status_code == status.HTTP_200_OK
    assert resp_put.json()["age"] == 34

    # Confirm update on disk
    with open(json_path, "r", encoding="utf-8") as f:
        file_data = json.load(f)
    assert file_data[0]["age"] == 34

    # Delete via DELETE
    resp_del = client.delete(f"/clients/{client_id}")
    assert resp_del.status_code == status.HTTP_204_NO_CONTENT

    # Confirm deletion on disk
    with open(json_path, "r", encoding="utf-8") as f:
        file_data = json.load(f)
    assert file_data == []

    # GET should now return 404
    resp_not_found = client.get(f"/clients/{client_id}")
    assert resp_not_found.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in resp_not_found.json()["detail"].lower()
