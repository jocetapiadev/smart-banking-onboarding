from fastapi.testclient import TestClient
from app.main import app
import io

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Smart Banking Onboarding Service Running"}

def test_analyze_document_valid_pdf():
    pdf_content = b"%PDF-1.4 dummy content"
    files = {"file": ("test_doc.pdf", io.BytesIO(pdf_content), "application/pdf")}
    
    response = client.post("/api/v1/analyze-document", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_doc.pdf"
    assert "risk_score" in data

def test_analyze_document_invalid_extension():
    files = {"file": ("test_doc.txt", io.BytesIO(b"dummy text"), "text/plain")}
    response = client.post("/api/v1/analyze-document", files=files)
    assert response.status_code == 400
