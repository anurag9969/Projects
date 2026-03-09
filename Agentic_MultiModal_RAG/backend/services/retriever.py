from typing import List, Dict
from backend.vectorstore.chroma_client import ChromaClient


class RetrieverService:

    def __init__(self):
        self.chroma_client = ChromaClient()

    def retrieve(self, question: str, doc_id: str, k: int = 5) -> List[Dict]:
        """
        Retrieve top-k relevant chunks from vector store.
        """

        results = self.chroma_client.query(
            query=question,
            doc_id=doc_id,
            k=k
        )

        return results