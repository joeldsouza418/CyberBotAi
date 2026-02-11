# app/rag_logic.py
import numpy as np
import os
import faiss
import pickle
from sklearn.metrics.pairwise import cosine_similarity

EMBED_DIR = "saved_embeddings"

def ensure_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def save_embeddings(doc_id, chunks, embeddings):
    ensure_dir(EMBED_DIR)
    meta = {"chunks": chunks}
    with open(os.path.join(EMBED_DIR, f"{doc_id}_meta.pkl"), "wb") as f:
        pickle.dump(meta, f)
    np.save(os.path.join(EMBED_DIR, f"{doc_id}_embeddings.npy"), embeddings)

def load_embeddings(doc_id):
    meta_path = os.path.join(EMBED_DIR, f"{doc_id}_meta.pkl")
    emb_path = os.path.join(EMBED_DIR, f"{doc_id}_embeddings.npy")
    if not os.path.exists(meta_path) or not os.path.exists(emb_path):
        return None
    with open(meta_path, "rb") as f:
        meta = pickle.load(f)
    embeddings = np.load(emb_path)
    return meta["chunks"], embeddings

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)  # inner product; use normalized vectors
    faiss.normalize_L2(embeddings)
    index.add(embeddings)
    return index

def retrieve_top_k(question_embedding, embeddings, chunks, k=5):
    # embeddings assumed normalized or use sklearn
    scores = cosine_similarity(question_embedding.reshape(1, -1), embeddings)[0]
    idx = np.argsort(scores)[::-1][:k]
    return [chunks[i] for i in idx], scores[idx]
