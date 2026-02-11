// src/api.js
const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function uploadPdf(file) {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch(`${BASE}/upload_pdf`, {
        method: "POST",
        body: form
    });
    return res.json();
}

export async function askQuestion(doc_id, question) {
    const res = await fetch(`${BASE}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doc_id, question })
    });
    return res.json();
}
