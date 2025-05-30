import uuid
from typing import List
from domain.client import Client
from dto.client_dto import ClientCreateRequest, ClientUpdateRequest
from repository.client_repository import ClientRepository


class ClientService:
    """
    Service layer for client business logic.
    Orchestrates operations between domain objects and repository.
    """

    def __init__(self, repository: ClientRepository):
        self.repository = repository

    def create_client(self, request: ClientCreateRequest) -> Client:
        """Create a new client with generated unique ID."""
        client_id = str(uuid.uuid4())
        client = Client(
            id=client_id,
            name=request.name,
            last_name=request.last_name,
            age=request.age
        )
        return self.repository.save(client)

    def get_client_by_id(self, client_id: str) -> Client:
        """Retrieve a client by their unique identifier."""
        client = self.repository.find_by_id(client_id)
        if not client:
            raise ValueError(f"Client with ID {client_id} not found")
        return client

    def get_all_clients(self) -> List[Client]:
        """Retrieve all clients from the system."""
        return self.repository.find_all()

    def update_client(self, client_id: str, request: ClientUpdateRequest) -> Client:
        """Update an existing client with new information."""
        client = self.get_client_by_id(client_id)
        client.update_fields(
            name=request.name,
            last_name=request.last_name,
            age=request.age
        )
        return self.repository.update(client)

    def delete_client(self, client_id: str) -> bool:
        """Delete a client from the system."""
        if not self.repository.find_by_id(client_id):
            raise ValueError(f"Client with ID {client_id} not found")
        return self.repository.delete(client_id)