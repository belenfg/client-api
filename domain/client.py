from datetime import datetime


class Client:
    """
    Domain model representing a client entity.
    Contains business logic and data structure for client operations.
    """

    def __init__(self, id: str, name: str, last_name: str, age: int):
        self.id = id
        self.name = name
        self.last_name = last_name
        self.age = age
        self.created_at = datetime.now().isoformat()

    def to_dict(self) -> dict:
        """Convert client object to dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "last_name": self.last_name,
            "age": self.age,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        """Create client object from dictionary data."""
        client = cls(data["id"], data["name"], data["last_name"], data["age"])
        client.created_at = data.get("created_at", datetime.now().isoformat())
        return client

    def update_fields(self, name: str = None, last_name: str = None, age: int = None):
        """Update client fields with provided values."""
        if name is not None:
            self.name = name
        if last_name is not None:
            self.last_name = last_name
        if age is not None:
            self.age = age