import json
import os
from typing import List, Optional
from domain.client import Client
from dotenv import load_dotenv

load_dotenv()
DEFAULT_FILE = os.getenv("CLIENTS_FILE", "clients.json")

class ClientRepository:
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or DEFAULT_FILE
        self._ensure_file_exists()


    def _ensure_file_exists(self) -> None:
        """Create the JSON file if it doesn't exist."""
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read_data(self) -> List[dict]:
        """Read data from JSON file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def _write_data(self, data: List[dict]) -> None:
        """Write data to JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def save(self, client: Client) -> Client:
        """Save a new client to the repository."""
        data = self._read_data()
        data.append(client.to_dict())
        self._write_data(data)
        return client

    def find_by_id(self, client_id: str) -> Optional[Client]:
        """Find a client by their unique identifier."""
        data = self._read_data()
        for item in data:
            if item["id"] == client_id:
                return Client.from_dict(item)
        return None

    def find_all(self) -> List[Client]:
        """Retrieve all clients from the repository."""
        data = self._read_data()
        return [Client.from_dict(item) for item in data]

    def update(self, client: Client) -> Client:
        """Update an existing client in the repository."""
        data = self._read_data()
        for i, item in enumerate(data):
            if item["id"] == client.id:
                data[i] = client.to_dict()
                self._write_data(data)
                return client
        raise ValueError(f"Client with ID {client.id} not found")

    def delete(self, client_id: str) -> bool:
        """Delete a client from the repository."""
        data = self._read_data()
        original_length = len(data)
        data = [item for item in data if item["id"] != client_id]
        if len(data) < original_length:
            self._write_data(data)
            return True
        return False