import React, { useState } from "react";
import UploadButton from "./components/UploadButton";
import ChatWindow from "./components/ChatWindow";

function App() {
  const [doc, setDoc] = useState(null);

  return (
    <div
      style={{
        height: "100vh",          // full viewport height
        width: "100vw",           // full viewport width
        background: "linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        fontFamily: "'Poppins', sans-serif",
        color: "#333",
        margin: 0,
        padding: 0,
        overflow: "hidden",
      }}
    >
      <div
        style={{
          background: "white",
          borderRadius: "16px",
          boxShadow: "0 8px 20px rgba(0,0,0,0.1)",
          padding: "32px",
          width: "90%",
          maxWidth: "900px",
          height: "90vh",          // card fills most of screen
          display: "flex",
          flexDirection: "column",
        }}
      >
        <h1
          style={{
            fontSize: "2rem",
            fontWeight: "600",
            color: "#3f51b5",
            marginBottom: "16px",
            textAlign: "center",
          }}
        >
          PDF RAG Chat
        </h1>

        <UploadButton onUploaded={(data) => setDoc(data)} />

        {doc && (
          <div
            style={{
              marginTop: "16px",
              background: "#f0f4ff",
              borderRadius: "8px",
              padding: "12px",
              fontSize: "0.95rem",
              color: "#2c387e",
              boxShadow: "inset 0 0 5px rgba(63,81,181,0.2)",
            }}
          >
            Uploaded doc id: <strong>{doc.doc_id}</strong>, chunks:{" "}
            <strong>{doc.n_chunks}</strong>
          </div>
        )}

        <div
          style={{
            marginTop: "24px",
            borderTop: "1px solid #e0e0e0",
            paddingTop: "16px",
            flex: 1,
            overflowY: "auto",
          }}
        >
          <ChatWindow docId={doc?.doc_id} />
        </div>
      </div>
    </div>
  );
}

export default App;
