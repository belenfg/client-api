import pytest
from dto.client_dto import ClientCreateRequest, ClientUpdateRequest, ClientResponse


def test_client_create_request_valid():
    """Test ClientCreateRequest validation with valid data."""
    data = {"name": "Alice", "last_name": "Smith", "age": 30}
    dto = ClientCreateRequest(**data)
    assert dto.name == "Alice"
    assert dto.last_name == "Smith"
    assert dto.age == 30


def test_client_create_request_invalid_age():
    """Test ClientCreateRequest validation fails for negative age."""
    with pytest.raises(ValueError):
        ClientCreateRequest(name="Bob", last_name="Jones", age=-5)


def test_client_update_request_optional_fields():
    """Test ClientUpdateRequest allows missing optional fields."""
    data = {}
    dto = ClientUpdateRequest(**data)
    assert dto.name is None
    assert dto.last_name is None
    assert dto.age is None


def test_client_response_fields():
    """Test ClientResponse creation and field assignment."""
    data = {"id": "123", "name": "Carol", "last_name": "Williams", "age": 45, "created_at": "2025-06-02T12:00:00Z"}
    dto = ClientResponse(**data)
    assert dto.id == "123"
    assert dto.name == "Carol"
    assert dto.last_name == "Williams"
    assert dto.age == 45
    assert dto.created_at == "2025-06-02T12:00:00Z"
