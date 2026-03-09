# Agentic Multimodal RAG Assistant

This project is an experiment I built to explore how **agentic AI systems and Retrieval-Augmented Generation (RAG)** work together in a practical application.

The idea is simple: upload a PDF document and ask questions about it. The assistant then decides the best way to answer the query by selecting the appropriate tool. It can either retrieve information from the uploaded document using vector search, perform a web search if external information is needed, or solve calculations if the query contains mathematical expressions.

The system then combines the retrieved context with a large language model to generate the final answer.

---

## What the Project Does

- Allows users to upload PDF documents
- Extracts and processes document text
- Stores document embeddings in a vector database
- Uses an agent-style router to decide how to answer queries
- Generates responses using an LLM
- Streams responses in a ChatGPT-like interface
- Shows reasoning traces and an execution graph so the internal workflow is visible

---

## How It Works

When a document is uploaded, the backend extracts the text and splits it into smaller chunks.  
Each chunk is converted into embeddings and stored in a vector database.

When the user asks a question, the system first decides **which tool to use**:

- Vector search for questions related to the uploaded document
- Web search for questions that require external information
- Calculator for mathematical queries

Relevant context is then passed to the language model to generate the final answer.

---

## Architecture

```
User Question
      │
      ▼
Tool Router
   ├ Vector Retrieval (RAG)
   ├ Web Search
   └ Calculator
      │
      ▼
Context Retrieval
      │
      ▼
LLM Answer Generation
      │
      ▼
Streaming Response
```

---

## Tech Stack

Frontend  
- Streamlit

Backend  
- FastAPI

AI / LLM  
- LangChain  
- OpenRouter API

Retrieval  
- ChromaDB  
- Sentence Transformers

Tools  
- DuckDuckGo Search  
- NumExpr

Visualization  
- Graphviz

---

## Project Structure

```
project/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   ├── services/
│   └── vectorstore/
│
├── frontend/
│   ├── streamlit_app.py
│   └── planner_agent.py
│
├── .env
└── requirements.txt
```

---

## Running the Project

Start the backend:

```
python -m uvicorn backend.main:app --reload
```

Start the frontend:

```
python -m streamlit run frontend/streamlit_app.py
```

Then open the UI, upload a PDF, and start asking questions.

---

## Why I Built This

I wanted to build a project that combines several concepts used in modern AI applications:

- Retrieval-Augmented Generation
- agent-style tool routing
- vector databases
- LLM-powered interfaces

This project helped me understand how these components work together to build intelligent assistants.

---
