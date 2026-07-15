from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from app.core.config import settings
from app.services.vector_store import search_documents
from app.schemas.chat import QueryResponse, SourceCitation

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.2
)

RAG_PROMPT = """You are a highly intelligent corporate document assistant. 
Your goal is to answer the user's question accurately based ONLY on the provided context below.

CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question using ONLY the provided context. If the answer is not contained in the context, say "I cannot find the answer in the provided documents."
2. ALWAYS cite the page number of the document where you found the information. Format citations like this: [Page X].
3. Be concise and professional.
"""

prompt_template = ChatPromptTemplate.from_template(RAG_PROMPT)

async def generate_answer(question: str) -> QueryResponse:
    """Retrieves context from Qdrant and generates an answer using Gemini."""
    
    # 1. Retrieve relevant chunks
    search_results = await search_documents(question, limit=4)
    
    if not search_results:
        return QueryResponse(
            answer="I could not find any relevant documents to answer your question.",
            sources=[]
        )
        
    # 2. Format Context
    context_pieces = []
    sources = []
    for idx, res in enumerate(search_results):
        text = res["text"]
        page = res["page_number"]
        doc_id = res["document_id"]
        
        context_pieces.append(f"--- CHUNK {idx + 1} (Page {page}) ---\n{text}\n")
        
        # Avoid duplicate source entries
        if not any(s.page_number == page and s.document_id == doc_id for s in sources):
            sources.append(
                SourceCitation(
                    document_id=doc_id,
                    page_number=page,
                    text_snippet=text[:100] + "..."  # snippet for reference
                )
            )
            
    full_context = "\n".join(context_pieces)
    
    # 3. Generate Answer
    chain = prompt_template | llm
    ai_msg = await chain.ainvoke({
        "context": full_context,
        "question": question
    })
    
    answer_text = str(ai_msg.content)
    
    # 4. Return formatted response
    return QueryResponse(
        answer=answer_text,
        sources=sources
    )
