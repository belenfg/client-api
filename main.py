import os
import uvicorn
from fastapi import FastAPI
from datetime import datetime
from controller.client_controller import client_router

# FastAPI application setup
app = FastAPI(
    title="Client Management API",
    description="RESTful API for client management using Domain-Driven Design principles",
    version="1.0.0",
    contact={
        "name": "API Support",
        "email": "support@clientapi.com",
    },
)

# Include client router
app.include_router(client_router)


@app.get("/health")
async def health_check():
    """Health check endpoint to verify API status."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Client Management API"
    }


@app.get("/")
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Welcome to Client Management API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=True)