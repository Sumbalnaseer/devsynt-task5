import { useEffect, useState } from "react";
import { api } from "../api";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.stats().then(setStats).catch((e) => setError(e.message));
  }, []);

  const cards = stats
    ? [
        { label: "Total Documents", value: stats.total_documents },
        { label: "Processed", value: stats.processed },
        { label: "Processing", value: stats.processing },
        { label: "Failed", value: stats.failed },
        { label: "Indexed Chunks", value: stats.total_indexed_chunks },
      ]
    : [];

  return (
    <div>
      <h1 className="page-title">Overview</h1>
      <p className="page-sub">Live status of your document knowledge base and chat activity.</p>

      {error && <div className="error-banner">Could not reach the backend: {error}</div>}

      {stats && (
        <div className="stat-row">
          {cards.map((c) => (
            <div className="stat-card" key={c.label}>
              <div className="stat-value">{c.value}</div>
              <div className="stat-label">{c.label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="panel">
        <h3 style={{ marginBottom: 10, fontSize: 16 }}>Questions asked</h3>
        <div className="stat-value" style={{ fontSize: 22 }}>
          {stats ? stats.total_questions : "—"}
        </div>
        <div className="stat-label">Total user questions sent to the chatbot across all sessions</div>
      </div>
    </div>
  );
}
