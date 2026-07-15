from fastapi import APIRouter, UploadFile, File, BackgroundTasks, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.db.models import Document, DocumentStatus
from app.schemas.document import DocumentResponse
from app.services.document_service import save_upload_file, process_document_task
import uuid

router = APIRouter()

@router.post("/", response_model=DocumentResponse, status_code=202)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # 1. Create a PENDING document in the database
    new_doc = Document(
        filename=file.filename,
        status=DocumentStatus.PENDING
    )
    # We assign an ID early so we can name the file securely
    new_doc.id = uuid.uuid4()
    
    # 2. Save the file to disk
    file_path = await save_upload_file(file, new_doc.id)
    new_doc.file_path = file_path
    
    db.add(new_doc)
    await db.commit()
    await db.refresh(new_doc)
    
    # 3. Trigger the background task for parsing
    background_tasks.add_task(process_document_task, new_doc.id, file_path, db)
    
    # 4. Return accepted response
    return new_doc
