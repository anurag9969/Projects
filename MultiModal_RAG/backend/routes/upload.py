import os
import shutil
from fastapi import APIRouter, UploadFile, File

from backend.services.parser import PDFParser
from backend.services.chunker import TextChunker
from backend.services.embedder import DocumentEmbedder

router = APIRouter()

UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Parse PDF
    parser = PDFParser(file_path)
    pages = parser.extract_text()

    # Chunk text
    chunker = TextChunker()
    chunks = chunker.create_chunks(pages)

    # Embed and store
    embedder = DocumentEmbedder()
    result = embedder.process_and_store(chunks)

    return {
        "message": "Document processed successfully",
        "document_id": result["doc_id"],
        "total_chunks": result["total_chunks"]
    }