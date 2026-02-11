import React, { useRef } from "react";
import { uploadPdf } from "../api";

export default function UploadButton({ onUploaded }) {
    const ref = useRef();

    async function handleFile(e) {
        const file = e.target.files[0];
        if (!file) return;
        const data = await uploadPdf(file);
        onUploaded(data); // {doc_id, n_chunks}
    }

    return (
        <div>
            <input ref={ref} type="file" accept="application/pdf" onChange={handleFile} style={{ display: "none" }} />
            <button onClick={() => ref.current.click()}>Upload PDF</button>
        </div>
    );
}
