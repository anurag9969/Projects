import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Multimodal PDF QA", layout="wide")

st.title("📄 Multimodal PDF Question Answering System")

# Session state for document id
if "document_id" not in st.session_state:
    st.session_state.document_id = None


# ------------------------
# Upload Section
# ------------------------

st.header("Upload PDF")

uploaded_file = st.file_uploader("Upload your document", type=["pdf"])

if uploaded_file is not None:

    if st.button("Process Document"):

        files = {"file": uploaded_file.getvalue()}

        response = requests.post(
            f"{API_URL}/upload",
            files={"file": uploaded_file}
        )

        if response.status_code == 200:

            data = response.json()

            st.session_state.document_id = data["document_id"]

            st.success("Document processed successfully!")

            st.write("Document ID:", data["document_id"])
            st.write("Total Chunks:", data["total_chunks"])

        else:
            st.error("Upload failed")


# ------------------------
# Question Section
# ------------------------

st.header("Ask Questions")

if st.session_state.document_id:

    question = st.text_input("Enter your question")

    if st.button("Ask"):

        payload = {
            "document_id": st.session_state.document_id,
            "question": question
        }

        response = requests.post(
            f"{API_URL}/query",
            json=payload
        )

        if response.status_code == 200:

            result = response.json()

            st.subheader("Answer")
            st.write(result["answer"])

            st.subheader("Sources")
            st.write(result["sources"])

            st.subheader("Confidence")
            st.write(result["confidence"])

        else:
            st.error("Query failed")

else:

    st.info("Upload a document first.")