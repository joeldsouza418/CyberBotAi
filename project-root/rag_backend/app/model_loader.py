# app/model_loader.py
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# load sentence-transformer for embeddings
EMBED_MODEL_NAME = "all-mpnet-base-v2"

def load_embedding_model(device="cpu"):
    model = SentenceTransformer(EMBED_MODEL_NAME, device=device)
    return model

# example: CoT generator (for reasoning)
COT_MODEL = "microsoft/Phi-3-mini-4k-instruct"   # adjust if needed
QA_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"  # adjust if needed

def load_llm(model_name, device="cpu"):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16 if device=="cuda" else None)
    model.to(device)
    return tokenizer, model
