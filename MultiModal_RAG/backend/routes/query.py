from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.retriever import RetrieverService
from backend.services.rag_chain import RAGChain

router = APIRouter()


class QueryRequest(BaseModel):
    document_id: str
    question: str


@router.post("/query")
def query_document(request: QueryRequest):

    retriever = RetrieverService()
    chunks = retriever.retrieve(
        question=request.question,
        doc_id=request.document_id
    )

    rag = RAGChain()
    answer = rag.generate_answer(
        question=request.question,
        chunks=chunks
    )

    return answer