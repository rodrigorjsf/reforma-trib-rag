# ReformaTax Backend

FastAPI backend for the ReformaTax citation-grounded Q&A system.

## Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your API keys
```

## Development

```bash
# Activate virtual environment
source .venv/bin/activate

# Run development server
uvicorn src.main:app --reload --port 3001
```

## API Endpoints

- `GET /health` - Health check
- `POST /api/query` - Submit a question
- `GET /api/user/{user_id}` - Get user info and rate limits

## API Documentation

When running, visit:
- Swagger UI: http://localhost:3001/docs
- ReDoc: http://localhost:3001/redoc
