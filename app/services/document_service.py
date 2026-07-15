import os
import fitz  # PyMuPDF
from uuid import UUID
from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.db.models import Document, DocumentStatus

DATA_DIR = "data"

async def save_upload_file(upload_file: UploadFile, document_id: UUID) -> str:
    """Saves the uploaded file to the local data directory securely."""
    os.makedirs(DATA_DIR, exist_ok=True)
    file_extension = os.path.splitext(upload_file.filename)[1] if upload_file.filename else ".pdf"
    file_path = os.path.join(DATA_DIR, f"{document_id}{file_extension}")
    
    with open(file_path, "wb") as buffer:
        while chunk := await upload_file.read(1024 * 1024):  # 1MB chunks
            buffer.write(chunk)
            
    return file_path

async def process_document_task(document_id: UUID, file_path: str, db: AsyncSession):
    """Background task to parse the PDF, extract text, and chunk it."""
    try:
        # Update status to PROCESSING
        doc = await db.get(Document, document_id)
        if not doc:
            return
        doc.status = DocumentStatus.PROCESSING
        await db.commit()

        # Parse PDF using PyMuPDF
        text_chunks = []
        try:
            with fitz.open(file_path) as pdf_doc:
                for page_num in range(len(pdf_doc)):
                    page = pdf_doc.load_page(page_num)
                    text = page.get_text("text")
                    if text.strip():
                        text_chunks.append({
                            "page_number": page_num + 1,
                            "text": text.strip()
                        })
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

        # Chunk the text using LangChain
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        final_chunks = []
        for chunk in text_chunks:
            splits = text_splitter.split_text(chunk["text"])
            for split in splits:
                final_chunks.append({
                    "document_id": str(document_id),
                    "page_number": chunk["page_number"],
                    "text": split
                })

        # Send `final_chunks` to Qdrant
        from app.services.vector_store import insert_document_chunks
        await insert_document_chunks(final_chunks)
        print(f"Document {document_id} successfully parsed into {len(final_chunks)} chunks and vectorized.")

        # Mark as completed
        doc.status = DocumentStatus.COMPLETED
        await db.commit()

    except Exception as e:
        # Mark as failed and record error
        doc = await db.get(Document, document_id)
        if doc:
            doc.status = DocumentStatus.FAILED
            doc.error_message = str(e)
            await db.commit()
        print(f"Error processing document {document_id}: {e}")
