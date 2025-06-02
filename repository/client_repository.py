import json
import os
from typing import List, Optional

from domain.client import Client
from dotenv import load_dotenv

from .exceptions import DuplicateClientError, ClientNotFoundError, RepositoryError


load_dotenv()
DEFAULT_FILE = os.getenv("CLIENTS_FILE", "clients.json")


class ClientRepository:
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path or DEFAULT_FILE
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the JSON file if it doesn't exist."""
        if not os.path.exists(self.file_path):
            try:
                with open(self.file_path, "w", encoding="utf-8") as f:
                    json.dump([], f)
            except OSError as e:
                raise RepositoryError(f"Unable to create {self.file_path}: {e}")

    def _read_data(self) -> List[dict]:
        """Read data from JSON file."""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # If file was removed externally, recreate it as empty list
            self._ensure_file_exists()
            return []
        except json.JSONDecodeError as e:
            # Could not parse JSON at all → treat as repository corruption
            raise RepositoryError(f"JSON decode error in {self.file_path}: {e}")
        except OSError as e:
            raise RepositoryError(f"Unable to read {self.file_path}: {e}")

    def _write_data(self, data: List[dict]) -> None:
        """Write data to JSON file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError as e:
            raise RepositoryError(f"Unable to write to {self.file_path}: {e}")

    def save(self, client: Client) -> Client:
        """
        Save a new client to the repository.
        Raises DuplicateClientError if a client with the same ID already exists.
        """
        all_data = self._read_data()

        # Check for existing ID
        if any(item.get("id") == client.id for item in all_data):
            raise DuplicateClientError(f"Client with ID {client.id} already exists")

        all_data.append(client.to_dict())
        self._write_data(all_data)
        return client

    def find_by_id(self, client_id: str) -> Optional[Client]:
        """Find a client by their unique identifier."""
        data = self._read_data()
        for item in data:
            if item.get("id") == client_id:
                return Client.from_dict(item)
        return None

    def find_all(self) -> List[Client]:
        """Retrieve all clients from the repository."""
        data = self._read_data()
        return [Client.from_dict(item) for item in data]

    def update(self, client: Client) -> Client:
        """
        Update an existing client in the repository.
        Raises ClientNotFoundError if the client ID does not exist.
        """
        data = self._read_data()
        for idx, item in enumerate(data):
            if item.get("id") == client.id:
                data[idx] = client.to_dict()
                self._write_data(data)
                return client

        # If we reach here, no matching ID was found
        raise ClientNotFoundError(f"Client with ID {client.id} not found")

    def delete(self, client_id: str) -> bool:
        """
        Delete a client from the repository.
        Returns True if deletion succeeded, False if the client was not found.
        (We do NOT raise if not found—service/controller can decide what to do.)
        """
        data = self._read_data()
        filtered = [item for item in data if item.get("id") != client_id]
        if len(filtered) == len(data):
            # No change → ID was not present
            return False

        # We removed something → overwrite file
        self._write_data(filtered)
        return True
