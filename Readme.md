# Study RAG Assistant

The Study RAG Assistant project is an intelligent retrieval-augmented generation system that allows you to upload documents, search for information, and get context-aware answers along with source references. The system uses a FastAPI backend and a Streamlit front-end to provide an interactive user experience.

## Features

- **Document Upload:** Upload various document types (PDF, TXT, JSON, PPT, PPTX) and process them for semantic search.
- **Semantic Search:** Retrieve relevant document sections using vector similarity search.
- **Question Answering:** Ask questions about your documents and get detailed, context-aware responses.
- **Interactive UI:** Use the Streamlit interface for chatting with your documents, managing uploads, and searching content.
- **API Endpoints:** A FastAPI server that provides endpoints for querying the system, document management, and more.

## Prerequisites

- Python 3.8 or higher
- pip

## Setup

1. **Clone the Repository:**

   ```bash
   git clone <repository-url>
   cd StudyRag

   python -m venv myenv
source myenv/bin/activate

# pip install -r requirements.txt


# uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# streamlit run streamlit_app.py