import os
import requests
import numexpr
from functools import lru_cache
from dotenv import load_dotenv
from duckduckgo_search import DDGS
from langchain_openai import ChatOpenAI

load_dotenv()

API_URL = "http://127.0.0.1:8000"

# Fast free model via OpenRouter
llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    max_tokens=512
)


# -------------------------
# VECTOR RAG TOOL
# -------------------------

@lru_cache(maxsize=128)
def vector_rag_tool(question, doc_id):

    try:

        r = requests.post(
            f"{API_URL}/query",
            json={
                "question": question,
                "document_id": doc_id
            },
            timeout=60
        )

        if r.status_code != 200:
            return ""

        data = r.json()

        if isinstance(data, dict):
            return data.get("answer", "")

        return str(data)

    except:
        return ""


# -------------------------
# WEB SEARCH TOOL
# -------------------------

def web_search_tool(query):

    results = []

    try:

        with DDGS() as ddgs:

            for r in ddgs.text(query, max_results=3):

                results.append(r["body"])

        return "\n".join(results)

    except:

        return ""


# -------------------------
# CALCULATOR TOOL
# -------------------------

def calculator_tool(expression):

    try:

        return str(numexpr.evaluate(expression))

    except:

        return ""


# -------------------------
# TOOL ROUTER
# -------------------------

def select_tool(question):

    q = question.lower()

    if any(x in q for x in ["calculate", "+", "-", "*", "/", "percentage"]):

        return "calculator"

    if any(x in q for x in ["latest", "news", "current", "today"]):

        return "web"

    return "vector"


# -------------------------
# MAIN AGENT
# -------------------------

def planner_executor_agent(question, doc_id):

    reasoning = []

    tool = select_tool(question)

    reasoning.append(f"Router selected tool → {tool}")

    if tool == "calculator":

        context = calculator_tool(question)

        reasoning.append("Calculator executed")

    elif tool == "web":

        context = web_search_tool(question)

        reasoning.append("Web search executed")

    else:

        context = vector_rag_tool(question, doc_id)

        reasoning.append("Vector RAG retrieval executed")

    prompt = f"""
Answer the question using the provided context.

Context:
{context}

Question:
{question}
"""

    reasoning.append("LLM generating final answer")

    response = llm.invoke(prompt)

    return {
        "answer": response.content,
        "tool_used": tool,
        "reasoning": reasoning,
        "context": context
    }