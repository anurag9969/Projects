import uuid
from typing import List, Dict

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from backend.config import settings


# -----------------------------
# Load embedding model ONCE
# -----------------------------
embedding_model = HuggingFaceEmbeddings(
    model_name=settings.EMBEDDING_MODEL
)


# -----------------------------
# Persistent Chroma database
# -----------------------------
vectorstore = Chroma(
    persist_directory=settings.CHROMA_PATH,
    embedding_function=embedding_model
)


class ChromaClient:
    """
    Handles all interactions with Chroma vector database.
    """

    def __init__(self):
        self.vectorstore = vectorstore

    # -----------------------------
    # Add documents to vector store
    # -----------------------------
    def add_documents(self, chunks: List[Dict], doc_id: str):
        """
        Store chunked documents in Chroma DB
        """

        documents = []

        for chunk in chunks:

            metadata = chunk["metadata"]

            metadata["doc_id"] = doc_id
            metadata["chunk_id"] = str(uuid.uuid4())

            documents.append(
                Document(
                    page_content=chunk["content"],
                    metadata=metadata
                )
            )

        self.vectorstore.add_documents(documents)
        self.vectorstore.persist()

    # -----------------------------
    # Query vector store
    # -----------------------------
    def query(self, query: str, doc_id: str, k: int = 3):
        """
        Retrieve top-k relevant chunks for a document
        """

        results = self.vectorstore.similarity_search(
            query=query,
            k=k,
            filter={"doc_id": doc_id}
        )

        formatted_results = []

        for doc in results:

            formatted_results.append({
                "content": doc.page_content,
                "page": doc.metadata.get("page"),
                "content_type": doc.metadata.get("content_type"),
                "score": None
            })

        return formatted_results