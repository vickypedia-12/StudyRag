import axios from "axios";

const API_URL = "http://localhost:8000"; // Change if backend is deployed elsewhere

export const getDocuments = () => axios.get(`${API_URL}/documents`);
export const uploadDocument = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return axios.post(`${API_URL}/upload`, formData);
};
export const deleteDocument = (filename) =>
  axios.delete(`${API_URL}/documents/${filename}`);
export const queryRAG = (question, max_sources = 3) =>
  axios.post(`${API_URL}/query`, { question, max_sources });
export const searchDocuments = (query, limit = 5) =>
  axios.get(`${API_URL}/search`, { params: { query, limit } });