import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ChatWithDocuments from "./components/ChatWithDocuments";
import UploadDocuments from "./components/UploadDocuments";
import ManageDocuments from "./components/ManageDocuments";
import SearchDocuments from "./components/SearchDocuments";

function App() {
  return (
    <Router>
      <nav>
        <Link to="/">Chat</Link> | <Link to="/upload">Upload</Link> | <Link to="/manage">Manage</Link> | <Link to="/search">Search</Link>
      </nav>
      <Routes>
        <Route path="/" element={<ChatWithDocuments />} />
        <Route path="/upload" element={<UploadDocuments />} />
        <Route path="/manage" element={<ManageDocuments />} />
        <Route path="/search" element={<SearchDocuments />} />
      </Routes>
    </Router>
  );
}

export default App;