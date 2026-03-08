from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:

    def __init__(self):

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=800,
            chunk_overlap=150,
            separators=["\n\n", "\n", ".", " ", ""]
        )

    def create_chunks(self, pages: List[Dict]) -> List[Dict]:

        chunks = []

        for page in pages:

            page_number = page["page"]
            content_type = page["content_type"]
            text = page["text"]

            split_texts = self.text_splitter.split_text(text)

            for idx, chunk in enumerate(split_texts):

                chunks.append({
                    "content": chunk,
                    "metadata": {
                        "page": page_number,
                        "chunk_index": idx,
                        "content_type": content_type
                    }
                })

        return chunks