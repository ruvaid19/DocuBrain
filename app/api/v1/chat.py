from fastapi import APIRouter
from app.schemas.chat import QueryRequest, QueryResponse
from app.services.rag_service import generate_answer

router = APIRouter()

@router.post(
    "/",
    response_model=QueryResponse,
    summary="Query the document knowledge base",
    description="Takes a user question, searches the Qdrant vector database for relevant text chunks, and uses Gemini 1.5 Flash to generate a conversational answer with exact page citations."
)
async def query_documents(request: QueryRequest):
    """
    Takes a user question, searches the vector database for relevant chunks,
    and returns a generated answer with citations.
    """
    response = await generate_answer(request.question)
    return response
