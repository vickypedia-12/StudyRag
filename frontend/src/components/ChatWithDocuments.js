import React, { useState } from "react";
import { queryRAG } from "../api";

export default function ChatWithDocuments() {
  const [question, setQuestion] = useState("");
  const [maxSources, setMaxSources] = useState(3);
  const [answer, setAnswer] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question) return;
    setLoading(true);
    setAnswer(null);
    setSources([]);
    try {
      const res = await queryRAG(question, maxSources);
      setAnswer(res.data.answer);
      setSources(res.data.sources || []);
      setHistory([{ question, answer: res.data.answer, sources: res.data.sources, time: new Date() }, ...history]);
    } catch (e) {
      setAnswer("Error: " + (e.response?.data?.detail || e.message));
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Chat with Your Documents</h2>
      <form onSubmit={handleSubmit}>
        <textarea
          rows={3}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question about your documents..."
          style={{ width: "100%" }}
        />
        <div>
          <label>
            Max Sources:
            <input
              type="number"
              min={1}
              max={10}
              value={maxSources}
              onChange={(e) => setMaxSources(Number(e.target.value))}
              style={{ width: 50, marginLeft: 5 }}
            />
          </label>
          <button type="submit" disabled={loading} style={{ marginLeft: 10 }}>
            {loading ? "Loading..." : "Submit"}
          </button>
        </div>
      </form>
      {answer && (
        <div>
          <h3>Answer</h3>
          <div>{answer}</div>
          <h4>Sources</h4>
          <ul>
            {sources.map((src, i) => (
              <li key={i}>
                <b>{src.source}</b>
                <pre style={{ whiteSpace: "pre-wrap" }}>{src.content}</pre>
              </li>
            ))}
          </ul>
        </div>
      )}
      {history.length > 0 && (
        <div>
          <h4>Previous Questions</h4>
          <ul>
            {history.slice(0, 5).map((item, i) => (
              <li key={i}>
                <b>Q:</b> {item.question}
                <br />
                <b>A:</b> {item.answer}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}