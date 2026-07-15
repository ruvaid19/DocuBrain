import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "project": "DocuBrain Enterprise RAG API"}

def test_upload_non_pdf_fails(client: TestClient):
    """Test that uploading a non-PDF file returns a 422 error from our custom handler."""
    # Create a fake text file
    file_content = b"This is a fake text file, not a PDF."
    
    response = client.post(
        "/api/v1/upload/",
        files={"file": ("fake.txt", file_content, "text/plain")}
    )
    
    assert response.status_code == 422
    json_resp = response.json()
    assert json_resp["error"] == "PDFParseError"
    assert "Only PDF files are supported" in json_resp["detail"]
