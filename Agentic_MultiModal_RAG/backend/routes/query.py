from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.agentic_rag import agent_graph


router = APIRouter()


class QueryRequest(BaseModel):
    document_id: str
    question: str


@router.post("/query")
def query_document(request: QueryRequest):

    result = agent_graph.invoke(
        {
            "question": request.question,
            "doc_id": request.document_id
        }
    )

    return {
        "answer": result["answer"]
    }