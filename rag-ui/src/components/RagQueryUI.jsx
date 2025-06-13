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
    <div style={{
      minHeight: "100vh",
      backgroundColor: "#fdd835",
      color: "#000",
      fontFamily: "Helvetica, Arial, sans-serif",
      padding: "4rem 2rem",
      textAlign: "center"
    }}>
      <h1 style={{ fontSize: "3rem", fontWeight: "900", marginBottom: "2rem" }}>
        Retrieval Augmented Generation.
      </h1>

      <div style={{ display: "flex", justifyContent: "center", flexWrap: "wrap", gap: "1rem" }}>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask your RAG assistant..."
          style={{
            padding: "1rem",
            fontSize: "1.2rem",
            width: "400px",
            maxWidth: "100%",
            border: "none",
            borderRadius: "0",
            borderBottom: "4px solid black",
            backgroundColor: "#fff",
            color: "#000",
            outline: "none",
          }}
        />
        <button
  onClick={handleQuery}
  disabled={loading}
  className="jiggle-button"
  style={{
    padding: "1rem 2rem",
    fontSize: "1rem",
    fontWeight: "bold",
    backgroundColor: "#000",
    color: "#fdd835",
    border: "none",
    cursor: "pointer",
  }}
>
  {loading ? "Processing..." : "Submit"}
</button>

      </div>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      <div style={{ marginTop: "3rem", maxWidth: "800px", marginInline: "auto", textAlign: "left" }}>
        {history.map((item, index) => (
          <div
            key={index}
            style={{
              backgroundColor: "#fff",
              color: "#000",
              padding: "1.5rem",
              borderRadius: "0.5rem",
              marginBottom: "1rem",
              boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
            }}
          >
            <p style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>Q: {item.query}</p>
            <p>A: {item.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RagQueryUI;
