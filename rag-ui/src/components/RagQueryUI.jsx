// === RagQueryUI.jsx ===

import React, { useState } from "react";

const RagQueryUI = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);

  const handleQuery = async () => {
    if (!query.trim()) {
      setError("Please enter a query.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) throw new Error("Server error");

      const data = await response.json();
      const newQA = {
        query,
        answer: data.answer || "No answer found.",
      };

      setHistory((prev) => [...prev, newQA]);
      setQuery("");
    } catch (err) {
      console.error("Fetch error:", err);
      setError("An error occurred while fetching the response.");
    }

    setLoading(false);
  };

  return (
    <div style={{ padding: "2rem", maxWidth: "800px", margin: "0 auto" }}>
      <h2>Ask Your RAG Assistant</h2>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask something like: 'Latest updates on AI in healthcare'"
        style={{
          width: "70%",
          padding: "0.75rem",
          fontSize: "1rem",
          border: "1px solid #ccc",
          borderRadius: "4px",
        }}
      />
      <button
        onClick={handleQuery}
        disabled={loading}
        style={{
          marginLeft: "1rem",
          padding: "0.75rem 1rem",
          fontSize: "1rem",
          backgroundColor: "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "4px",
          cursor: "pointer",
        }}
      >
        {loading ? "Processing..." : "Submit"}
      </button>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      <div style={{ marginTop: "2rem" }}>
        {history.map((item, index) => (
          <div
            key={index}
            style={{
              background: "#f8f9fa",
              padding: "1rem",
              borderRadius: "8px",
              border: "1px solid #ddd",
              marginBottom: "1rem",
            }}
          >
            <p><strong>Q:</strong> {item.query}</p>
            <p><strong>A:</strong> {item.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RagQueryUI;
