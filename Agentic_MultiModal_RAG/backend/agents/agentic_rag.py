from typing import TypedDict, List

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from backend.config import settings
from backend.services.retriever import RetrieverService


llm = ChatOpenAI(
    model=settings.LLM_MODEL,
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY,
    temperature=0
)


retriever = RetrieverService()


class AgentState(TypedDict):
    question: str
    rewritten_question: str
    context: List
    answer: str
    validation: str


# ----------------------------
# Query Rewriter Agent
# ----------------------------

def rewrite_query(state: AgentState):

    prompt = f"""
Rewrite the user question to improve document retrieval.

Question:
{state['question']}
"""

    response = llm.invoke(prompt)

    return {"rewritten_question": response.content}


# ----------------------------
# Retrieval Agent
# ----------------------------

def retrieve_docs(state: AgentState):

    docs = retriever.retrieve(
        question=state["rewritten_question"],
        doc_id=state["doc_id"]
    )

    return {"context": docs}


# ----------------------------
# Answer Generation Agent
# ----------------------------

def generate_answer(state: AgentState):

    context_text = "\n\n".join(
        [f"(Page {d['page']}) {d['content']}" for d in state["context"]]
    )

    prompt = f"""
Answer the question using ONLY the context.

Context:
{context_text}

Question:
{state['question']}
"""

    response = llm.invoke(prompt)

    return {"answer": response.content}


# ----------------------------
# Validation Agent
# ----------------------------

def validate_answer(state: AgentState):

    prompt = f"""
Check if the answer is grounded in the provided context.

Answer:
{state['answer']}

If grounded return: VALID
If hallucinated return: RETRY
"""

    response = llm.invoke(prompt)

    return {"validation": response.content}


# ----------------------------
# Decision Router
# ----------------------------

def router(state: AgentState):

    if "VALID" in state["validation"]:
        return END
    else:
        return "rewrite_query"


# ----------------------------
# Build Graph
# ----------------------------

def build_agent():

    workflow = StateGraph(AgentState)

    workflow.add_node("rewrite_query", rewrite_query)
    workflow.add_node("retrieve_docs", retrieve_docs)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("validate_answer", validate_answer)

    workflow.set_entry_point("rewrite_query")

    workflow.add_edge("rewrite_query", "retrieve_docs")
    workflow.add_edge("retrieve_docs", "generate_answer")
    workflow.add_edge("generate_answer", "validate_answer")

    workflow.add_conditional_edges(
        "validate_answer",
        router
    )

    return workflow.compile()


agent_graph = build_agent()