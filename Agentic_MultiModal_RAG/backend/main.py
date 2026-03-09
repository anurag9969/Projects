from fastapi import FastAPI
from backend.routes import upload, query

app = FastAPI(title="Multimodal PDF RAG API")

app.include_router(upload.router)
app.include_router(query.router)


@app.get("/")
def root():
    return {"message": "Multimodal PDF QA API running"}