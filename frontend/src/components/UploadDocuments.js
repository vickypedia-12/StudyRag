import React, { useState } from "react";
import { uploadDocument, getDocuments } from "../api";

export default function UploadDocuments({ onUpload }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("");

  const handleUpload = async () => {
    if (!file) return;
    setStatus("Uploading...");
    try {
      await uploadDocument(file);
      setStatus("Upload successful!");
      onUpload && onUpload();
    } catch (e) {
      setStatus("Upload failed.");
    }
  };

  return (
    <div>
      <h2>Upload Documents</h2>
      <input
        type="file"
        accept=".pdf,.txt,.json,.ppt,.pptx"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button onClick={handleUpload}>Upload</button>
      <div>{status}</div>
    </div>
  );
}