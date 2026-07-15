from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1 import upload
from app.services.vector_store import ensure_collection_exists

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    await ensure_collection_exists()
    yield
    # Shutdown logic
    pass

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}

# Include routers
app.include_router(upload.router, prefix=f"{settings.API_V1_STR}/upload", tags=["upload"])
# app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
