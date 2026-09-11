import { useEffect, useRef, useState } from "react";
import { api } from "../api";

function fmtTime(iso) {
  try {
    return new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return "";
  }
}

export default function Chat() {
  const [sessions, setSessions] = useState([]);
  const [activeId, setActiveId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef(null);

  const loadSessions = async () => {
    const list = await api.listSessions();
    setSessions(list);
    return list;
  };

  const startNewSession = async () => {
    const s = await api.newSession("New Chat");
    await loadSessions();
    setActiveId(s.session_id);
    setMessages([]);
  };

  useEffect(() => {
    loadSessions().then((list) => {
      if (list.length > 0) setActiveId(list[0].session_id);
    });
  }, []);

  useEffect(() => {
    if (activeId) api.getMessages(activeId).then(setMessages).catch(() => {});
  }, [activeId]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const send = async () => {
    if (!input.trim()) return;
    let sessionId = activeId;
    if (!sessionId) {
      const s = await api.newSession("New Chat");
      await loadSessions();
      sessionId = s.session_id;
      setActiveId(sessionId);
    }
    const question = input;
    setInput("");
    setError("");
    setMessages((m) => [...m, { role: "user", content: question, created_at: new Date().toISOString(), sources: [] }]);
    setLoading(true);
    try {
      const result = await api.sendMessage(sessionId, question);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: result.answer, sources: result.sources, created_at: new Date().toISOString() },
      ]);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="page-title">Chat</h1>
      <p className="page-sub">Ask questions grounded in your uploaded documents.</p>

      <div className="chat-layout">
        <div className="session-list">
          <button className="btn" style={{ width: "100%", marginBottom: 10 }} onClick={startNewSession}>
            + New Chat
          </button>
          {sessions.map((s) => (
            <div
              key={s.session_id}
              className={`session-item ${s.session_id === activeId ? "active" : ""}`}
              onClick={() => setActiveId(s.session_id)}
            >
              {s.title || "Chat"}
            </div>
          ))}
        </div>

        <div className="chat-window">
          <div className="messages">
            {messages.length === 0 && !loading && (
              <div style={{ color: "var(--ink-soft)", fontSize: 14 }}>
                Ask something like "What is the commission fee for selling a home?"
              </div>
            )}
            {messages.map((m, i) => (
              <div key={i} className={`msg ${m.role}`}>
                <div>{m.content}</div>
                {m.sources && m.sources.length > 0 && (
                  <div className="sources">
                    Sources:
                    {m.sources.map((s, j) => (
                      <span className="source-chip" key={j}>
                        📄 {s.document_name} · p.{s.page_number}
                      </span>
                    ))}
                  </div>
                )}
                <div className="msg-time">{fmtTime(m.created_at)}</div>
              </div>
            ))}
            {loading && <div className="loading-dot">Thinking…</div>}
            {error && <div className="error-banner">{error}</div>}
            <div ref={bottomRef} />
          </div>
          <div className="chat-input-row">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && send()}
              placeholder="Type your question…"
              disabled={loading}
            />
            <button className="btn" onClick={send} disabled={loading || !input.trim()}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
