import React, { useState } from "react";

const RagQueryUI = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [history, setHistory] = useState([]);
  const [darkMode, setDarkMode] = useState(false); // 🌗 Dark mode state

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

  const bgColor = darkMode ? "#3D5A40" : "#fdd835";
  const textColor = darkMode ? "#f1f1f1" : "#000";
  const btnBg = darkMode ? "#fff" : "#000";
  const btnColor = darkMode ? "#3D5A40" : "#fdd835";
  const inputBg = darkMode ? "#e0e0e0" : "#fff";

  return (
    <div
      style={{
        minHeight: "100vh",
        backgroundColor: bgColor,
        color: textColor,
        fontFamily: "Helvetica, Arial, sans-serif",
        padding: "4rem 2rem",
        textAlign: "center",
        transition: "all 0.4s ease",
      }}
    >
      {/* Dark mode toggle button */}
      <button
        onClick={() => setDarkMode(!darkMode)}
        style={{
          position: "absolute",
          top: "1rem",
          right: "1rem",
          padding: "0.5rem 1rem",
          borderRadius: "8px",
          border: "none",
          cursor: "pointer",
          backgroundColor: btnBg,
          color: btnColor,
          fontWeight: "bold",
          boxShadow: "0 2px 5px rgba(0,0,0,0.2)",
        }}
      >
        {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
      </button>

      <h1
        style={{ fontSize: "2.5rem", fontWeight: "900", marginBottom: "2rem" }}
      >
        The news. Now with answers.
      </h1>

      <div
        style={{
          display: "flex",
          justifyContent: "center",
          flexWrap: "wrap",
          gap: "1rem",
        }}
      >
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
            borderBottom: `4px solid ${textColor}`,
            backgroundColor: inputBg,
            color: "#000",
            outline: "none",
            borderRadius: "12px",
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
            backgroundColor: btnBg,
            color: btnColor,
            border: "none",
            cursor: "pointer",
            borderRadius: "12px",
            transition: "transform 0.2s ease",
          }}
        >
          {loading ? "Processing..." : "Submit"}
        </button>
      </div>

      {error && <p style={{ color: "red", marginTop: "1rem" }}>{error}</p>}

      <div
        style={{
          marginTop: "3rem",
          maxWidth: "800px",
          marginInline: "auto",
          textAlign: "left",
        }}
      >
        {history.map((item, index) => (
          <div
            key={index}
            style={{
              backgroundColor: inputBg,
              color: "#000",
              padding: "1.5rem",
              borderRadius: "0.5rem",
              marginBottom: "1rem",
              boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
            }}
          >
            <p style={{ fontWeight: "bold", marginBottom: "0.5rem" }}>
              Q: {item.query}
            </p>
            <p>A: {item.answer}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RagQueryUI;
