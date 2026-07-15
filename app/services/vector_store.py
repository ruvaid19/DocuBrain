import uuid
from typing import List, Dict, Any
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models as rest
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.core.config import settings

COLLECTION_NAME = "docubrain_vectors"
VECTOR_SIZE = 768  # Standard size for text-embedding-004

# Initialize Qdrant Client
qdrant_client = AsyncQdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY,
)

# Initialize Gemini Embeddings
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=settings.GEMINI_API_KEY
)

async def ensure_collection_exists():
    """Checks if the Qdrant collection exists and creates it if it doesn't."""
    collections_response = await qdrant_client.get_collections()
    collection_names = [col.name for col in collections_response.collections]
    
    if COLLECTION_NAME not in collection_names:
        print(f"Creating Qdrant collection: {COLLECTION_NAME}")
        await qdrant_client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=rest.VectorParams(
                size=VECTOR_SIZE,
                distance=rest.Distance.COSINE
            )
        )
    else:
        print(f"Qdrant collection {COLLECTION_NAME} already exists.")

async def insert_document_chunks(chunks: List[Dict[str, Any]]):
    """Generates embeddings and inserts chunks into Qdrant."""
    if not chunks:
        return
        
    texts = [chunk["text"] for chunk in chunks]
    
    # Generate embeddings
    # We use await aembed_documents for async embedding generation
    vectors = await embeddings.aembed_documents(texts)
    
    # Prepare Qdrant points
    points = []
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        point_id = str(uuid.uuid4())
        payload = {
            "document_id": chunk["document_id"],
            "page_number": chunk["page_number"],
            "text": chunk["text"]
        }
        points.append(
            rest.PointStruct(
                id=point_id,
                vector=vector,
                payload=payload
            )
        )
        
    # Insert points into Qdrant
    await qdrant_client.upsert(
        collection_name=COLLECTION_NAME,
        points=points
    )
    print(f"Successfully inserted {len(points)} vectors into Qdrant.")
