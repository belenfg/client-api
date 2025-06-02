import pytest
from domain.client import Client


def test_client_initialization_valid():
    """Test that a Client can be initialized with valid data."""
    client = Client(id=1, name="Alice", last_name="Wonderland", age=30)
    assert client.id == 1
    assert client.name == "Alice"
    assert client.last_name == "Wonderland"
    assert client.age == 30
