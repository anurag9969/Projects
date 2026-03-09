from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from backend.config import settings


class RAGChain:

    def __init__(self):

        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.OPENROUTER_API_KEY,
            temperature=0
        )

        self.prompt = ChatPromptTemplate.from_template("""
You are a document question answering assistant.

Use ONLY the provided context to answer the question.

If the answer is not present in the context, say:
"Answer not found in document."

Provide response in this format:

Answer:
<answer>

Sources:
<page numbers>

Confidence:
<number between 0 and 1>

Context:
{context}

Question:
{question}
""")

    def build_context(self, chunks: List[Dict]) -> str:

        context_parts = []

        for chunk in chunks:
            page = chunk["page"]
            content = chunk["content"]

            context_parts.append(f"(Page {page}) {content}")

        return "\n\n".join(context_parts)

    def generate_answer(self, question: str, chunks: List[Dict]) -> Dict:

        context = self.build_context(chunks)

        chain = self.prompt | self.llm

        response = chain.invoke({
            "context": context,
            "question": question
        })

        return {
            "answer": response.content,
            "sources": [chunk["page"] for chunk in chunks],
            "confidence": 0.85
        }