import uuid
from typing import List, Dict

from backend.vectorstore.chroma_client import ChromaClient


class DocumentEmbedder:
    """
    Handles embedding and storing document chunks into Chroma vector DB.
    """

    def __init__(self):
        self.chroma_client = ChromaClient()

    def process_and_store(self, chunks: List[Dict]) -> Dict:
        """
        Process chunks and store them in the vector database.

        Args:
            chunks (List[Dict]): List of chunk dictionaries from the chunker.

        Returns:
            Dict: document_id and number of stored chunks
        """

        # Generate unique document id
        doc_id = str(uuid.uuid4())

        # Add documents to vector database
        self.chroma_client.add_documents(chunks, doc_id)

        return {
            "doc_id": doc_id,
            "total_chunks": len(chunks)
        }

    def store_existing_doc(self, chunks: List[Dict], doc_id: str) -> Dict:
        """
        Store chunks under an existing document id (optional use case).

        Args:
            chunks (List[Dict]): chunk data
            doc_id (str): existing document id

        Returns:
            Dict
        """

        self.chroma_client.add_documents(chunks, doc_id)

        return {
            "doc_id": doc_id,
            "total_chunks": len(chunks)
        }