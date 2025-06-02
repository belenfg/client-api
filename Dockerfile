# Official lightweight Python image as base
FROM python:3.11-slim

# Set an environment variable to prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Copy only requirements first (cache optimization)
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose a port (if your app listens on one; e.g. 8000 for Uvicorn/FastAPI)
EXPOSE 8000

# Default command to run your application.
CMD ["python", "main.py"]
