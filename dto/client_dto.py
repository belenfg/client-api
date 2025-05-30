from pydantic import BaseModel, Field
from typing import Optional


class ClientCreateRequest(BaseModel):
    """DTO for client creation requests."""
    name: str = Field(..., min_length=1, max_length=100, description="Client's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Client's last name")
    age: int = Field(..., ge=0, le=150, description="Client's age")


class ClientUpdateRequest(BaseModel):
    """DTO for client update requests."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Client's first name")
    last_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Client's last name")
    age: Optional[int] = Field(None, ge=0, le=150, description="Client's age")


class ClientResponse(BaseModel):
    """DTO for client response data."""
    id: str = Field(..., description="Unique client identifier")
    name: str = Field(..., description="Client's first name")
    last_name: str = Field(..., description="Client's last name")
    age: int = Field(..., description="Client's age")
    created_at: str = Field(..., description="Creation timestamp")