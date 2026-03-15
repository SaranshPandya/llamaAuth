# llamaAuth

Authentication layer for Ollama servers.

`llamaAuth` is a small FastAPI service that sits in front of an Ollama server and adds user registration, login, API key generation, and authenticated access to Ollama.

## Features

- User registration
- Login with username or email
- API key generation
- API key based authentication
- Forward authenticated requests to Ollama
- Configurable Ollama base URL

## API Endpoints

### `POST /register`

Creates a new user.

**Request**
```json
{
  "username": "saransh",
  "email": "saransh@example.com",
  "password": "strong-password",
  "age": 23
}
```

### `POST /login`

Authenticates a user using username or email.

**Request**
```json
{
  "username": "saransh",
  "password": "strong-password"
}
```

or

```json
{
  "email": "saransh@example.com",
  "password": "strong-password"
}
```

### `POST /get_api`

Generates an API key for an authenticated user.

**Request**
```json
{
  "username": "saransh",
  "password": "strong-password"
}
```

### `POST /chat`

Authenticates the API key and forwards the request to Ollama.

**Request**
```json
{
  "query": "Explain transformers simply.",
  "api_key": "sk_xxxxxxxxxxxxxxxxxxxxxxxxx",
  "model": "llama3.2",
  "stream": false,
  "base_url": "http://localhost:11434"
}
```

## Project Structure

```text
llamaAuth/
├── core/
│   ├── api/
│   │   └── endpoints.py
│   ├── cache/
│   │   └── cache.py
│   └── encrypt/
│       ├── api_key_generator.py
│       └── encryption.py
├── database_hander/
│   ├── databasehander.py
│   └── queries.json
├── schemas/
│   └── packet.py
├── scripts/
│   ├── migrate.py
│   └── migrations/
├── main.py
├── pyproject.toml
└── uv.lock
```

## Requirements

- Python 3.12+
- PostgreSQL

## Installation

```bash
git clone https://github.com/SaranshPandya/llamaAuth.git
cd llamaAuth
```

Using `uv`:

```bash
uv venv
source .venv/bin/activate
uv sync
```

Or with `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Environment Variables

Create a `.env` file in the project root:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
DBNAME=llamaauth
POSTGRES_SSLMODE=prefer
QUERY_PATH=database_hander/queries.json
```

## Running the Server
With uv:

```bash
uv run main.py
```

Or with python:

```bash
python main.py
```

Or with Uvicorn:

```bash
uvicorn main:_app --host 0.0.0.0 --port 5000
```

## Example Usage

### Register

```bash
curl -X POST "http://localhost:5000/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "saransh",
    "email": "saransh@example.com",
    "password": "strong-password",
    "age": 23
  }'
```

### Login

```bash
curl -X POST "http://localhost:5000/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "saransh",
    "password": "strong-password"
  }'
```

### Generate API Key

```bash
curl -X POST "http://localhost:5000/get_api" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "saransh",
    "password": "strong-password"
  }'
```

### Chat via Ollama

```bash
curl -X POST "http://localhost:5000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Write a short paragraph about black holes.",
    "api_key": "sk_your_generated_api_key",
    "model": "llama3.2",
    "stream": false,
    "base_url": "http://localhost:11434"
  }'
```

## License

Apache License 2.0
