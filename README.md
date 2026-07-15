# DocuBrain API

Enterprise RAG API built with FastAPI, PostgreSQL, and Qdrant.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start infrastructure (Postgres & Qdrant):
   ```bash
   docker-compose up -d
   ```

4. Apply migrations:
   ```bash
   alembic upgrade head
   ```

5. Run API:
   ```bash
   uvicorn app.main:app --reload
   ```
