import { useEffect, useRef, useState } from "react";
import { api } from "../api";

function fmtDate(iso) {
  try {
    return new Date(iso).toLocaleString();
  } catch {
    return iso;
  }
}

export default function Documents() {
  const [docs, setDocs] = useState([]);
  const [error, setError] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);
  const fileInput = useRef(null);
  const pollRef = useRef(null);

  const load = () => api.listDocuments().then(setDocs).catch((e) => setError(e.message));

  useEffect(() => {
    load();
    // Poll while anything is still processing, so status updates live
    pollRef.current = setInterval(() => {
      setDocs((current) => {
        if (current.some((d) => d.status === "processing")) load();
        return current;
      });
    }, 3000);
    return () => clearInterval(pollRef.current);
  }, []);

  const handleFiles = async (files) => {
    setError("");
    setUploading(true);
    try {
      for (const file of files) {
        const ext = file.name.split(".").pop().toLowerCase();
        if (!["pdf", "docx", "txt"].includes(ext)) {
          setError(`Unsupported file type: .${ext} (allowed: pdf, docx, txt)`);
          continue;
        }
        await api.uploadDocument(file);
      }
      load();
    } catch (e) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragActive(false);
    handleFiles(Array.from(e.dataTransfer.files));
  };

  return (
    <div>
      <h1 className="page-title">Documents</h1>
      <p className="page-sub">Upload, monitor, and manage the files powering the chatbot's knowledge base.</p>

      {error && <div className="error-banner">{error}</div>}

      <div
        className={`dropzone ${dragActive ? "drag" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
        onDragLeave={() => setDragActive(false)}
        onDrop={onDrop}
        onClick={() => fileInput.current.click()}
        style={{ cursor: "pointer" }}
      >
        {uploading ? "Uploading…" : "Drag & drop a PDF, DOCX, or TXT file here, or click to browse"}
        <input
          ref={fileInput}
          type="file"
          accept=".pdf,.docx,.txt"
          multiple
          hidden
          onChange={(e) => handleFiles(Array.from(e.target.files))}
        />
      </div>

      <div className="panel" style={{ padding: 0 }}>
        <table>
          <thead>
            <tr>
              <th>File</th>
              <th>Type</th>
              <th>Status</th>
              <th>Chunks</th>
              <th>Uploaded</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {docs.length === 0 && (
              <tr><td colSpan={6} style={{ color: "var(--ink-soft)", padding: 18 }}>No documents uploaded yet.</td></tr>
            )}
            {docs.map((d) => (
              <tr key={d.document_id}>
                <td>{d.filename}</td>
                <td>{d.file_type.toUpperCase()}</td>
                <td>
                  <span className={`badge ${d.status}`}>{d.status}</span>
                  {d.status === "failed" && d.error_message && (
                    <div style={{ fontSize: 11, color: "var(--err)", marginTop: 3 }}>{d.error_message}</div>
                  )}
                </td>
                <td>{d.chunk_count}</td>
                <td>{fmtDate(d.uploaded_at)}</td>
                <td style={{ whiteSpace: "nowrap" }}>
                  <button
                    className="btn secondary"
                    style={{ padding: "5px 10px", fontSize: 12, marginRight: 6 }}
                    onClick={() => api.reprocessDocument(d.document_id).then(load)}
                  >
                    Re-process
                  </button>
                  <button
                    className="btn danger"
                    style={{ padding: "5px 10px", fontSize: 12 }}
                    onClick={() => api.deleteDocument(d.document_id).then(load)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
