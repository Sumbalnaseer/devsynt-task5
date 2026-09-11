const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

async function req(path, options = {}) {
  const res = await fetch(`${API_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${res.status})`);
  }
  return res.json();
}

export const api = {
  stats: () => req("/api/dashboard/stats"),
  listDocuments: () => req("/api/documents"),
  deleteDocument: (id) => req(`/api/documents/${id}`, { method: "DELETE" }),
  reprocessDocument: (id) => req(`/api/documents/${id}/reprocess`, { method: "POST" }),
  uploadDocument: (file) => {
    const form = new FormData();
    form.append("file", file);
    return req("/api/documents/upload", { method: "POST", body: form });
  },
  newSession: (title) =>
    req("/api/chat/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    }),
  listSessions: () => req("/api/chat/sessions"),
  getMessages: (sessionId) => req(`/api/chat/sessions/${sessionId}/messages`),
  sendMessage: (sessionId, question) =>
    req("/api/chat/message", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, question }),
    }),
};
