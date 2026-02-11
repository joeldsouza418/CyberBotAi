import React, { useState } from "react";
import { askQuestion } from "../api";

export default function ChatWindow({ docId }) {
    const [messages, setMessages] = useState([]); // {sender, text}
    const [q, setQ] = useState("");
    const [loading, setLoading] = useState(false);

    async function send() {
        if (!q.trim()) return;
        const userMsg = { sender: "user", text: q };
        setMessages(m => [...m, userMsg]);
        setLoading(true);
        try {
            const res = await askQuestion(docId, q);
            // res may contain prompt + context or the LLM answer if integrated
            const answer = res.answer || res.prompt || JSON.stringify(res);
            setMessages(m => [...m, { sender: "bot", text: answer }]);
        } catch (err) {
            setMessages(m => [...m, { sender: "bot", text: "Error: " + err.message }]);
        } finally {
            setQ("");
            setLoading(false);
        }
    }

    return (
        <div>
            <div style={{ height: 400, overflow: 'auto', border: '1px solid #ccc', padding: 10 }}>
                {messages.map((m, i) => (
                    <div key={i} style={{ textAlign: m.sender === 'user' ? 'right' : 'left', margin: 6 }}>
                        <div style={{ display: "inline-block", padding: "8px 12px", borderRadius: 8, background: m.sender === 'user' ? "#e6f7ff" : "#f4f4f5" }}>
                            {m.text}
                        </div>
                    </div>
                ))}
            </div>

            <div style={{ display: "flex", marginTop: 8 }}>
                <input value={q} onChange={e => setQ(e.target.value)} placeholder="Ask a question..." style={{ flex: 1, padding: 8 }} />
                <button onClick={send} disabled={loading || !docId} style={{ marginLeft: 8 }}>
                    {loading ? "Thinking..." : "Send"}
                </button>
            </div>
        </div>
    );
}
