import os
from repository.client_repository import ClientRepository


def test_repository_file_creation(tmp_path):
    """
    When instantiating ClientRepository with a new file path,
    it should create the JSON file with an empty list.
    """
    file_path = tmp_path / "clients_infra.json"
    repo = ClientRepository(str(file_path))

    # The file should now exist
    assert os.path.exists(str(file_path))

    # The file content should be an empty JSON array
    with open(str(file_path), "r", encoding="utf-8") as f:
        content = f.read().strip()
    assert content == "[]"
