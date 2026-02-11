from fpdf import FPDF
import os
from app.model_loader import load_llm
from app.rag_logic import load_embeddings, retrieve_top_k
from app.model_loader import load_embedding_model
import numpy as np

# Load models
print("🔹 Loading models for report generation...")
EMBED_MODEL = load_embedding_model(device="cpu")
qg_tokenizer, qg_model = load_llm("microsoft/Phi-3-mini-4k-instruct")  # for question gen
qa_tokenizer, qa_model = load_llm("TinyLlama/TinyLlama-1.1B-Chat-v1.0")  # for answering


def generate_questions(text, n=5):
    """Generate analytical questions using CoT model"""
    prompt = (
        f"Read the following document context and generate {n} insightful questions "
        "that summarize the main points, methodology, and conclusions:\n\n"
        f"{text[:3000]}\n\nQuestions:"
    )

    inputs = qg_tokenizer(prompt, return_tensors="pt")
    outputs = qg_model.generate(**inputs, max_new_tokens=150)
    raw_text = qg_tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    # Extract each line as a question
    questions = [q.strip("-•1234567890. ") for q in raw_text.split("\n") if "?" in q]
    return questions[:n]


def answer_question(question, chunks, embeddings):
    """Retrieve relevant context and answer using QA model"""
    q_emb = EMBED_MODEL.encode([question], convert_to_numpy=True)
    q_emb = q_emb / (np.linalg.norm(q_emb, axis=1, keepdims=True) + 1e-10)
    top_chunks, _ = retrieve_top_k(q_emb, embeddings, chunks, k=3)
    context = "\n\n".join(top_chunks)
    
    prompt = (
        f"Context:\n{context}\n\nQuestion: {question}\n"
        "Answer concisely and clearly based on the context only."
    )
    inputs = qa_tokenizer(prompt, return_tensors="pt")
    outputs = qa_model.generate(**inputs, max_new_tokens=200)
    answer = qa_tokenizer.decode(outputs[0], skip_special_tokens=True)
    return answer


def build_pdf_report(filename, qna_pairs, title="Auto Q&A Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, title, ln=True, align="C")
    pdf.set_font("Arial", size=12)
    
    for i, (q, a) in enumerate(qna_pairs, 1):
        pdf.multi_cell(0, 10, f"\nQ{i}: {q}")
        pdf.multi_cell(0, 10, f"A{i}: {a}")
    
    pdf.output(filename)
    return filename


def generate_report(doc_id: str, n_questions: int = 5):
    """Main pipeline: loads doc, generates Qs, answers them, saves report"""
    loaded = load_embeddings(doc_id)
    if loaded is None:
        raise FileNotFoundError("Document not found.")
    chunks, embeddings = loaded
    full_text = " ".join(chunks)
    
    questions = generate_questions(full_text, n=n_questions)
    qna_pairs = []
    for q in questions:
        ans = answer_question(q, chunks, embeddings)
        qna_pairs.append((q, ans))
    
    os.makedirs("reports", exist_ok=True)
    filename = os.path.join("reports", f"{doc_id}_report.pdf")
    build_pdf_report(filename, qna_pairs)
    return filename, qna_pairs
