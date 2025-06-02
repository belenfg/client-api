import os
import sys
import json
import pytest

# --------------------------------------------------------------
# Add project root to sys.path so that "import main" will work
# --------------------------------------------------------------
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from fastapi.testclient import TestClient
from fastapi import status

from main import app
from repository.client_repository import ClientRepository
from controller.client_controller import get_client_repository


@pytest.fixture(autouse=True)
def clear_and_override(tmp_path):
    """
    Clear any existing dependency overrides and configure the repository
    to use a temporary JSON file for each test.
    """
    app.dependency_overrides = {}
    temp_file = tmp_path / "clients_func.json"
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


def test_full_flow_end_to_end(client, tmp_path):
    """
    Full end-to-end CRUD flow using FastAPI TestClient,
    persisting data in a temporary JSON file.
    """
    # 1. Create a new client
    create_response = client.post(
        "/clients", json={"name": "Alice", "last_name": "Wonderland", "age": 30}
    )
    assert create_response.status_code == status.HTTP_201_CREATED
    created_data = create_response.json()
    client_id = created_data["id"]

    # Confirm that the JSON file contains the new client
    json_path = tmp_path / "clients_func.json"
    with open(json_path, "r", encoding="utf-8") as f:
        file_content = json.load(f)
    assert isinstance(file_content, list)
    assert len(file_content) == 1
    assert file_content[0]["id"] == client_id

    # 2. Retrieve the client by ID
    get_response = client.get(f"/clients/{client_id}")
    assert get_response.status_code == status.HTTP_200_OK
    get_data = get_response.json()
    assert get_data["id"] == client_id
    assert get_data["name"] == "Alice"
    assert get_data["last_name"] == "Wonderland"
    assert get_data["age"] == 30

    # 3. List all clients
    list_response = client.get("/clients")
    assert list_response.status_code == status.HTTP_200_OK
    clients_list = list_response.json()
    assert isinstance(clients_list, list)
    assert any(item["id"] == client_id for item in clients_list)

    # 4. Update the client's age
    update_response = client.put(
        f"/clients/{client_id}", json={"age": 31}
    )
    assert update_response.status_code == status.HTTP_200_OK
    updated_data = update_response.json()
    assert updated_data["age"] == 31

    # Confirm persistence: read file and check age update
    with open(json_path, "r", encoding="utf-8") as f:
        file_content = json.load(f)
    assert file_content[0]["age"] == 31

    # 5. Verify update via GET
    verify_response = client.get(f"/clients/{client_id}")
    assert verify_response.status_code == status.HTTP_200_OK
    verify_data = verify_response.json()
    assert verify_data["age"] == 31

    # 6. Delete the client
    delete_response = client.delete(f"/clients/{client_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_response.content == b""

    # Confirm the JSON file is now empty
    with open(json_path, "r", encoding="utf-8") as f:
        file_content = json.load(f)
    assert file_content == []

    # 7. Verify deletion: GET should return 404
    final_response = client.get(f"/clients/{client_id}")
    assert final_response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in final_response.json()["detail"].lower()
