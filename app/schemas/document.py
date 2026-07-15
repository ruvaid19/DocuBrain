from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.db.models import DocumentStatus

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    upload_time: datetime
    status: DocumentStatus
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
