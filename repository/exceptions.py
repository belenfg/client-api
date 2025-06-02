# repository/exceptions.py

class RepositoryError(Exception):
    """Generic repository error (e.g. JSON parse failure, I/O error)."""


class DuplicateClientError(RepositoryError):
    """Raised when attempting to save a client whose ID already exists."""


class ClientNotFoundError(RepositoryError):
    """Raised when attempting to update/delete a client that does not exist."""
