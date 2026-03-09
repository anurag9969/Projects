import os
import requests
import numexpr

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from duckduckgo_search import DDGS

API_URL = "http://127.0.0.1:8000"

llm = ChatOpenAI(
    model="meta-llama/llama-3.1-8b-instruct:free",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    max_tokens=512
)

# -------------------------
# Tools
# -------------------------

def vector_search_tool(question, doc_id):

    r = requests.post(
        f"{API_URL}/query",
        json={
            "question": question,
            "document_id": doc_id
        }
    )

    return r.json()


def web_search_tool(query):

    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=3):
            results.append(r["body"])

    return "\n".join(results)


def calculator_tool(expression):

    try:
        return str(numexpr.evaluate(expression))
    except:
        return "invalid calculation"


# -------------------------
# State
# -------------------------

class AgentState(dict):
    question: str
    context: str
    answer: str
    decision: str
    doc_id: str


# -------------------------
# Query Rewriter
# -------------------------

def rewrite_query(state):

    prompt = f"""
Rewrite this question to improve retrieval:

{state['question']}
"""

    response = llm.invoke(prompt)

    return {"question": response.content}


# -------------------------
# Tool Selector
# -------------------------

def choose_tool(state):

    prompt = f"""
You are an AI assistant.

Decide which tool to use.

Available tools:

1 vector_search
2 web_search
3 calculator

Question:
{state['question']}

Respond with tool name only.
"""

    decision = llm.invoke(prompt)

    return {"decision": decision.content.strip()}


# -------------------------
# Tool Executor
# -------------------------

def run_tool(state):

    tool = state["decision"]

    if "vector" in tool:
        result = vector_search_tool(state["question"], state["doc_id"])

        return {"context": str(result)}

    elif "web" in tool:
        result = web_search_tool(state["question"])

        return {"context": result}

    elif "calculator" in tool:
        result = calculator_tool(state["question"])

        return {"context": result}

    return {"context": ""}


# -------------------------
# Answer Generator
# -------------------------

def generate_answer(state):

    prompt = f"""
Answer using the context.

Context:
{state['context']}

Question:
{state['question']}
"""

    response = llm.invoke(prompt)

    return {"answer": response.content}


# -------------------------
# Self Reflection
# -------------------------

def validate_answer(state):

    prompt = f"""
Check if the answer is grounded in the context.

Answer:
{state['answer']}

If good return VALID
If hallucinated return RETRY
"""

    result = llm.invoke(prompt)

    return {"decision": result.content}


# -------------------------
# Router
# -------------------------

def router(state):

    if "VALID" in state["decision"]:
        return END
    else:
        return "rewrite"


# -------------------------
# Build Graph
# -------------------------

def build_agent():

    graph = StateGraph(AgentState)

    graph.add_node("rewrite", rewrite_query)
    graph.add_node("choose_tool", choose_tool)
    graph.add_node("run_tool", run_tool)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("validate", validate_answer)

    graph.set_entry_point("rewrite")

    graph.add_edge("rewrite", "choose_tool")
    graph.add_edge("choose_tool", "run_tool")
    graph.add_edge("run_tool", "generate_answer")
    graph.add_edge("generate_answer", "validate")

    graph.add_conditional_edges(
        "validate",
        router
    )

    return graph.compile()


agent_graph = build_agent()