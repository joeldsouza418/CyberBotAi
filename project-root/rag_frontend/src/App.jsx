import React, { useState } from "react";
import UploadButton from "./components/UploadButton";
import ChatWindow from "./components/ChatWindow";

function App() {
  const [doc, setDoc] = useState(null);

  return (
    <div style={{ padding: 24, maxWidth: 800, margin: "0 auto" }}>
      <h1>PDF RAG Chat</h1>
      <UploadButton onUploaded={data => setDoc(data)} />
      {doc && <div style={{ marginTop: 12 }}>Uploaded doc id: {doc.doc_id}, chunks: {doc.n_chunks}</div>}
      <div style={{ marginTop: 16 }}>
        <ChatWindow docId={doc?.doc_id} />
      </div>
    </div>
  );
}

export default App;
