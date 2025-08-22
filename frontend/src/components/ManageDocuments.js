import React, { useEffect, useState } from "react";
import { getDocuments, deleteDocument } from "../api";

export default function ManageDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState("");

  const loadDocs = async () => {
    setLoading(true);
    try {
      const res = await getDocuments();
      setDocuments(res.data.documents || []);
    } catch (e) {
      setStatus("Failed to load documents.");
    }
    setLoading(false);
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleDelete = async (filename) => {
    setStatus(`Deleting ${filename}...`);
    try {
      await deleteDocument(filename);
      setStatus(`Deleted ${filename}`);
      loadDocs();
    } catch (e) {
      setStatus("Delete failed.");
    }
  };

  return (
    <div>
      <h2>Manage Documents</h2>
      <button onClick={loadDocs}>Refresh</button>
      <div>{status}</div>
      {loading ? (
        <div>Loading...</div>
      ) : documents.length === 0 ? (
        <div>No documents found.</div>
      ) : (
        <ul>
          {documents.map((doc) => (
            <li key={doc.filename}>
              <b>{doc.filename}</b> ({(doc.size_bytes / 1024).toFixed(1)} KB)
              <button onClick={() => handleDelete(doc.filename)} style={{ marginLeft: 10 }}>
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}