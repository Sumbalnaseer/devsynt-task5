import { useState } from "react";
import Dashboard from "./components/Dashboard";
import Documents from "./components/Documents";
import Chat from "./components/Chat";

const PAGES = {
  dashboard: { label: "Overview", component: Dashboard },
  documents: { label: "Documents", component: Documents },
  chat: { label: "Chat", component: Chat },
};

export default function App() {
  const [page, setPage] = useState("dashboard");
  const Page = PAGES[page].component;

  return (
    <div className="app-shell">
      <div className="sidebar">
        <div className="brand">Harborview</div>
        <div className="brand-sub">Document Intelligence</div>
        {Object.entries(PAGES).map(([key, { label }]) => (
          <div
            key={key}
            className={`nav-item ${page === key ? "active" : ""}`}
            onClick={() => setPage(key)}
          >
            {label}
          </div>
        ))}
      </div>
      <div className="main">
        <Page />
      </div>
    </div>
  );
}
