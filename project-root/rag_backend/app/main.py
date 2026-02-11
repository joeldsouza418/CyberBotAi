# app/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.pdf_utils import extract_text_from_pdf, chunk_text
from app.model_loader import load_embedding_model
from app.rag_logic import save_embeddings, load_embeddings, retrieve_top_k
import uuid
import numpy as np
import io
from fastapi.responses import FileResponse
from app.report_generator import generate_report


app = FastAPI()

# CORS for local dev - update origins for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# load embedding model on startup
from fastapi import BackgroundTasks
EMBED_MODEL = load_embedding_model(device="cpu")

@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF allowed")

    contents = await file.read()

    # ✅ create uploads folder if not exists
    import os
    os.makedirs("uploads", exist_ok=True)
    tmp_path = os.path.join("uploads", f"{uuid.uuid4().hex}.pdf")

    # ✅ save file locally
    with open(tmp_path, "wb") as f:
        f.write(contents)

    # process PDF as before
    text = extract_text_from_pdf(tmp_path)
    chunks = chunk_text(text, chunk_size=400, overlap=50)
    embeddings = EMBED_MODEL.encode(chunks, convert_to_numpy=True, show_progress_bar=False)

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    embeddings = embeddings / (norms + 1e-10)

    doc_id = uuid.uuid4().hex
    save_embeddings(doc_id, chunks, embeddings)
    return {"doc_id": doc_id, "n_chunks": len(chunks)}


@app.post("/ask")
async def ask(question: dict):
    # request body: {"doc_id": "...", "question": "..." }
    doc_id = question.get("doc_id")
    q_text = question.get("question")
    if not doc_id or not q_text:
        raise HTTPException(status_code=400, detail="doc_id and question required")

    # load embeddings
    loaded = load_embeddings(doc_id)
    if loaded is None:
        raise HTTPException(status_code=404, detail="doc not found")
    chunks, embeddings = loaded

    # embed the question
    q_emb = EMBED_MODEL.encode([q_text], convert_to_numpy=True)
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-10)

    top_chunks, scores = retrieve_top_k(q_emb, embeddings, chunks, k=5)
    # build prompt for the QA LLM (we will call external or local LLM here)
    prompt = "Use the following context to answer the question. Context:\n\n"
    for i, c in enumerate(top_chunks):
        prompt += f"Chunk {i+1}:\n{c}\n\n"
    prompt += f"Question: {q_text}\nAnswer (concise):"

    # for now, return prompt (replace with actual LLM call)
    return {"prompt": prompt, "context_chunks": top_chunks, "scores": scores.tolist()}

@app.post("/generate_report")
async def generate_report_api(payload: dict):
    doc_id = payload.get("doc_id")
    if not doc_id:
        raise HTTPException(status_code=400, detail="doc_id required")
    try:
        pdf_path, qna_pairs = generate_report(doc_id)
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{doc_id}_report.pdf"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
