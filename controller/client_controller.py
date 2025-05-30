from fastapi import APIRouter, HTTPException, Depends
from typing import List
from dto.client_dto import ClientCreateRequest, ClientUpdateRequest, ClientResponse
from service.client_service import ClientService
from repository.client_repository import ClientRepository


# Dependency injection functions
def get_client_repository() -> ClientRepository:
    """Dependency injection for client repository."""
    return ClientRepository()


def get_client_service(repository: ClientRepository = Depends(get_client_repository)) -> ClientService:
    """Dependency injection for client service."""
    return ClientService(repository)


# Router setup
client_router = APIRouter(prefix="/clients", tags=["clients"])


@client_router.get("", response_model=List[ClientResponse])
async def get_clients(service: ClientService = Depends(get_client_service)):
    """Get all clients from the system."""
    try:
        clients = service.get_all_clients()
        return [ClientResponse(**client.to_dict()) for client in clients]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@client_router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: str, service: ClientService = Depends(get_client_service)):
    """Get a specific client by their ID."""
    try:
        client = service.get_client_by_id(client_id)
        return ClientResponse(**client.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@client_router.post("", response_model=ClientResponse, status_code=201)
async def create_client(
    request: ClientCreateRequest,
    service: ClientService = Depends(get_client_service)
):
    """Create a new client in the system."""
    try:
        client = service.create_client(request)
        return ClientResponse(**client.to_dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@client_router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    request: ClientUpdateRequest,
    service: ClientService = Depends(get_client_service)
):
    """Update an existing client's information."""
    try:
        client = service.update_client(client_id, request)
        return ClientResponse(**client.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@client_router.delete("/{client_id}", status_code=204)
async def delete_client(client_id: str, service: ClientService = Depends(get_client_service)):
    """Delete a client from the system."""
    try:
        service.delete_client(client_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))