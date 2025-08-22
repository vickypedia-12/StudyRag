import React, { useState } from "react";
import { searchDocuments } from "../api";

export default function SearchDocuments() {
  const [query, setQuery] = useState("");
  const [limit, setLimit] = useState(5);
  const [results, setResults] = useState([]);
  const [status, setStatus] = useState("");

  const handleSearch = async () => {
    if (!query) return;
    setStatus("Searching...");
    setResults([]);
    try {
      const res = await searchDocuments(query, limit);
      setResults(res.data.results || []);
      setStatus("");
    } catch (e) {
      setStatus("Search failed.");
    }
  };

  return (
    <div>
      <h2>Search Documents</h2>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Enter search terms..."
        style={{ width: "60%" }}
      />
      <input
        type="number"
        min={1}
        max={20}
        value={limit}
        onChange={(e) => setLimit(Number(e.target.value))}
        style={{ width: 60, marginLeft: 10 }}
      />
      <button onClick={handleSearch} style={{ marginLeft: 10 }}>
        Search
      </button>
      <div>{status}</div>
      {results.length > 0 && (
        <div>
          <h4>Results</h4>
          <ul>
            {results.map((item, i) => (
              <li key={i}>
                <b>{item.source}</b>
                <pre style={{ whiteSpace: "pre-wrap" }}>{item.content}</pre>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}