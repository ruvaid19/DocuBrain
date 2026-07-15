from fastapi import HTTPException, status

class DocuBrainException(HTTPException):
    """Base exception class for DocuBrain API."""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class DocumentNotFoundError(DocuBrainException):
    def __init__(self, document_id: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with ID {document_id} not found."
        )

class PDFParseError(DocuBrainException):
    def __init__(self, detail: str = "Failed to parse the PDF file. It might be corrupted."):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )

class VectorStoreError(DocuBrainException):
    def __init__(self, detail: str = "Failed to communicate with the vector database."):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )
