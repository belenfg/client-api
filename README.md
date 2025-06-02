# Client Management API

A RESTful API built with FastAPI following Domain-Driven Design (DDD) principles for managing client information.

## 🏗️ Architecture

This project implements **Domain-Driven Design (DDD)** with clear separation of concerns:

- **Domain Layer**: Core business entities and logic
- **Repository Layer**: Data access and persistence
- **Service Layer**: Application business logic and orchestration
- **Controller Layer**: HTTP request handling and API endpoints
- **DTO Layer**: Data Transfer Objects for API communication

## 📁 Project Structure

```
client-api/
├── README.md             # Project documentation
├── .gitignore            # Git ignore rules
├── .dockerignore         # Docker ignore rules
├── Dockerfile            # Containerization instructions
├── requirements.txt      # Python dependencies
├── main.py               # FastAPI application entry point
├── domain/               # Domain models (e.g., client.py)
├── dto/                  # Data Transfer Objects (e.g., client_dto.py)
├── repository/           # Data persistence layer (ClientRepository, etc.)
├── service/              # Business logic layer (client_service.py)
├── controller/           # API endpoints (FastAPI routers)
└── tests/                # Unit and integration tests
```

## 🚀 Features

- **CRUD Operations**: Complete Create, Read, Update, Delete operations for clients
- **Data Validation**: Input validation using Pydantic models
- **Error Handling**: Comprehensive error handling with appropriate HTTP status codes
- **Auto Documentation**: Automatic API documentation with Swagger UI
- **Dependency Injection**: Clean dependency injection pattern
- **File-based Storage**: JSON file as mock database for simplicity
- **Health Check**: Health monitoring endpoint

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Root endpoint with API information |
| `GET` | `/health` | Health check endpoint |
| `GET` | `/clients` | Get all clients |
| `GET` | `/clients/{id}` | Get client by ID |
| `POST` | `/clients` | Create new client |
| `PUT` | `/clients/{id}` | Update existing client |
| `DELETE` | `/clients/{id}` | Delete client |

## 📋 Client Data Model

```json
{
  "id": "string (UUID)",
  "name": "string (1-100 chars)",
  "last_name": "string (1-100 chars)",
  "age": "integer (0-150)",
  "created_at": "string (ISO datetime)"
}
```

## 🛠️ Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Docker (for containerization)


## 📦 Installation

1. **Clone or download the project**
   ```bash
   # If using git
   git clone https://github.com/belenfg/client-api.git
   cd client-api
   
   # Or extract the ZIP file and navigate to the folder
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Build the Docker image**
   ```bash
   docker build -t my-python-app:latest .
   ```

## 🏃‍♂️ Running the Application

1. **Start the development server**
   ```bash
   python main.py
   ```
   
   Or alternatively:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the application**
   - **API Base URL**: http://localhost:8000
   - **Interactive Documentation**: http://localhost:8000/docs
   - **Alternative Documentation**: http://localhost:8000/redoc
   - **Health Check**: http://localhost:8000/health
   
3. **Running with Docker**
   - If you have already built the Docker image (my-python-app:latest), run:
   ```bash
   docker run --rm -d -p 8000:8000 --name client-api-container my-python-app:latest
   ```


## 📝 Usage Examples

### Create a Client
```bash
curl -X POST "http://localhost:8000/clients" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "John",
       "last_name": "Doe",
       "age": 30
     }'
```

### Get All Clients
```bash
curl -X GET "http://localhost:8000/clients"
```

### Get Client by ID
```bash
curl -X GET "http://localhost:8000/clients/{client_id}"
```

### Update a Client
```bash
curl -X PUT "http://localhost:8000/clients/{client_id}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Jane",
       "age": 25
     }'
```

### Delete a Client
```bash
curl -X DELETE "http://localhost:8000/clients/{client_id}"
```

## 🗄️ Data Storage

The application uses a JSON file (`clients.json`) as a mock database. This file is automatically created in the project root directory when the application runs for the first time.

**Note**: This is a development/demo setup. For production use, consider integrating with a proper database (PostgreSQL, MySQL, MongoDB, etc.).

## 🔧 Configuration

You can modify the following settings in the respective files:

- **Server Configuration**: Edit `main.py` to change host, port, or other server settings
- **Database File**: Modify the `file_path` parameter in `ClientRepository` constructor
- **Validation Rules**: Update validation constraints in `dto/client_dto.py`

## 🧪 Testing the API

1. **Using Swagger UI**: Navigate to http://localhost:8000/docs for interactive testing
2. **Using curl**: Use the examples provided above
3. **Using Postman**: Import the API endpoints using the OpenAPI specification available at http://localhost:8000/openapi.json


## 🧪 Testing the API

1. **Using Swagger UI**  
   Navigate to http://localhost:8000/docs for interactive testing.
2. **Using curl**  
   Use the examples provided above to exercise your endpoints from the command line.
3. **Using Postman**  
   Import the API endpoints via the OpenAPI specification at http://localhost:8000/openapi.json.

### 🧩 Running Tests with pytest Locally

Execute all unit and integration tests with pytest:

```bash
pytest --maxfail=1 --disable-warnings -q
```

## 🐳 Running Tests via Docker

Once you have built the Docker image (`my-python-app:latest`), run:

```bash
docker run --rm \
  -v "$(pwd)":/app \
  -w /app \
  my-python-app:latest \
  pytest --maxfail=1 -q
```

* `-v "$(pwd)":/app` mounts your local project (including `tests/`) into `/app` inside the container.
* `-w /app` sets `/app` as the working directory before running pytest.
* `--rm` removes the container after tests complete.

This command allows the container to use the pre-installed dependencies to execute pytest in isolation within Docker.


## 🚨 Error Handling

The API provides comprehensive error responses:

- **400 Bad Request**: Invalid input data
- **404 Not Found**: Client not found
- **422 Unprocessable Entity**: Validation errors
- **500 Internal Server Error**: Server-side errors

Example error response:
```json
{
  "detail": "Client with ID abc123 not found"
}
```

## 🔒 Security Considerations

This is a development/demo application. For production deployment, consider implementing:

- Authentication and authorization
- Rate limiting
- Input sanitization
- HTTPS encryption
- Request/response logging
- Data encryption at rest

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Change port in main.py or kill the process using the port
   lsof -ti:8000 | xargs kill -9  # macOS/Linux
   ```

2. **Module Import Errors**
   ```bash
   # Ensure you're in the project root directory
   # and virtual environment is activated
   ```

3. **Permission Issues with JSON File**
   ```bash
   # Ensure the application has write permissions in the project directory
   ```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Domain-Driven Design Principles](https://martinfowler.com/bliki/DomainDrivenDesign.html)

## 📄 License

This project is provided as-is for educational and development purposes.

---

**Happy Coding! 🎉**