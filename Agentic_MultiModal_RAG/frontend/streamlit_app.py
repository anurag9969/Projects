import streamlit as st
import time
import graphviz
import requests

from planner_agent import planner_executor_agent

API_URL = "http://127.0.0.1:8000"

st.set_page_config(layout="wide")

st.title("Agentic Multimodal RAG Assistant")

# -------------------------
# SESSION STATE
# -------------------------

if "document_id" not in st.session_state:
    st.session_state.document_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------
# SIDEBAR - DOCUMENT UPLOAD
# -------------------------

st.sidebar.header("Document Upload")

uploaded_file = st.sidebar.file_uploader("Upload PDF", type=["pdf"])

if uploaded_file:

    if st.sidebar.button("Process Document"):

        files = {"file": uploaded_file}

        response = requests.post(
            f"{API_URL}/upload",
            files=files
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.document_id = data["document_id"]

            st.sidebar.success("Document processed")

            st.sidebar.write("Chunks:", data["total_chunks"])

        else:

            st.sidebar.error("Upload failed")


# -------------------------
# ASK QUESTION
# -------------------------

st.header("Ask Questions")

question = st.text_input("Enter your question")

if st.button("Ask") and question:

    if not st.session_state.document_id:

        st.warning("Upload a document first")

        st.stop()

    start_time = time.time()

    result = planner_executor_agent(
        question,
        st.session_state.document_id
    )

    answer = result["answer"]
    reasoning = result["reasoning"]
    tool = result["tool_used"]
    context = result["context"]

    # -------------------------
    # STREAMING ANSWER
    # -------------------------

    st.subheader("Answer")

    placeholder = st.empty()

    text = ""

    for token in answer.split():

        text += token + " "

        placeholder.write(text)

        time.sleep(0.01)

    st.caption(f"Tool used → {tool}")

    latency = round(time.time() - start_time, 2)

    st.sidebar.metric("Latency", latency)

    # -------------------------
    # AGENT REASONING TRACE
    # -------------------------

    with st.expander("Agent Reasoning Trace"):

        for step in reasoning:

            st.write("•", step)

    # -------------------------
    # EXECUTION GRAPH
    # -------------------------

    graph = graphviz.Digraph()

    graph.node("User", "User Question")
    graph.node("Router", "Tool Router")
    graph.node("Tool", tool)
    graph.node("LLM", "Answer Generator")

    graph.edge("User", "Router")
    graph.edge("Router", "Tool")
    graph.edge("Tool", "LLM")

    st.subheader("Agent Execution Graph")

    st.graphviz_chart(graph)

    # -------------------------
    # CONTEXT VIEW
    # -------------------------

    with st.expander("Retrieved Context"):

        st.write(context)

    # -------------------------
    # STORE HISTORY
    # -------------------------

    st.session_state.chat_history.append(
        {"question": question, "answer": answer}
    )

# -------------------------
# CONVERSATION HISTORY
# -------------------------

if st.session_state.chat_history:

    st.subheader("Conversation History")

    for chat in st.session_state.chat_history:

        st.write("User:", chat["question"])
        st.write("Assistant:", chat["answer"])
        st.write("---")