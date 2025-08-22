import streamlit as st
import requests
import os
import json
from datetime import datetime
import time

# API URL - change if your API is running on a different host/port
API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="StudyRAG Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .source-box {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stButton button {
        width: 100%;
    }
    .upload-section {
        padding: 1rem;
        border: 2px dashed #4e8df5;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .file-item {
        padding: 0.5rem;
        border-bottom: 1px solid #e6e6e6;
        display: flex;
        justify-content: space-between;
    }
    .file-item:hover {
        background-color: #f0f2f6;
    }
    .navbar {
        display: flex;
        padding: 0.5rem;
        gap: 0.25rem;
        margin-bottom: 1rem;
    }
    .nav-item {
        text-align: center;
        padding: 0.5rem 0;
        border-radius: 0.25rem;
    }
    .nav-button {
        border: none;
        background: none;
        width: 100%;
    }
    .suggestion-item {
        padding: 0.5rem;
        border-bottom: 1px solid #e6e6e6;
        cursor: pointer;
    }
    .suggestion-item:hover {
        background-color: #f0f2f6;
    }
    .faq-item {
        margin-bottom: 1rem;
        border-left: 3px solid #4e8df5;
        padding-left: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'current_response' not in st.session_state:
    st.session_state.current_response = None
if 'documents' not in st.session_state:
    st.session_state.documents = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = None
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Chat with Documents"
if 'recent_searches' not in st.session_state:
    st.session_state.recent_searches = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'filtered_suggestions' not in st.session_state:
    st.session_state.filtered_suggestions = []


faq_data = [
    {
        "question": "How do I upload a document?",
        "answer": "Navigate to the 'Upload Documents' tab, click the file upload area, select your document (PDF, TXT, JSON, PPT, PPTX), and click 'Process Document'."
    },
    {
        "question": "What happens when I upload a document?",
        "answer": "The document is split into smaller chunks, converted to vector embeddings, and stored in a database for semantic search and retrieval."
    },
    {
        "question": "How do I ask questions about my documents?",
        "answer": "Use the 'Chat with Documents' tab. Type your question in the text area and click 'Submit Question'."
    },
    {
        "question": "How does the search function work?",
        "answer": "The search function uses semantic similarity to find relevant sections in your documents, even if they don't contain the exact search terms."
    },
    {
        "question": "Can I delete documents I've uploaded?",
        "answer": "Yes, go to the 'Manage Documents' tab where you can see all uploaded documents and delete them if needed."
    }
]

def load_documents():
    """Load documents from the API"""
    try:
        response = requests.get(f"{API_URL}/documents")
        if response.status_code == 200:
            st.session_state.documents = response.json()["documents"]
            return response.json()["documents"]
        else:
            st.error(f"Error loading documents: {response.text}")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")
        return []

def delete_document(filename):
    """Delete a document via the API"""
    try:
        response = requests.delete(f"{API_URL}/documents/{filename}")
        if response.status_code == 200:
            st.success(f"Deleted {filename}")
            # Refresh document list
            load_documents()
        else:
            st.error(f"Error deleting document: {response.text}")
    except Exception as e:
        st.error(f"Error connecting to API: {str(e)}")

def format_timestamp(timestamp):
    """Format a timestamp into a readable date string"""
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

def format_size(size_bytes):
    """Format file size in a human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def change_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

def update_search_suggestions():
    """Update search suggestions based on current query"""
    if st.session_state.current_page == "Chat with Documents":
        query = st.session_state.chat_input.lower()
    else:
        query = st.session_state.search_query.lower()
        
    if not query:
        st.session_state.filtered_suggestions = []
        return
    
    # Combine recent searches and previous questions for suggestions
    all_suggestions = set()
    
    # Add recent searches
    for search in st.session_state.recent_searches:
        all_suggestions.add(search)
    
    # Add previous questions
    for item in st.session_state.query_history:
        all_suggestions.add(item["question"])
    
    # Filter suggestions based on query
    st.session_state.filtered_suggestions = [
        suggestion for suggestion in all_suggestions 
        if query in suggestion.lower()
    ][:5]  # Limit to 5 suggestions

def use_suggestion(suggestion):
    """Use a suggestion as the query"""
    if st.session_state.current_page == "Chat with Documents":
        st.session_state.chat_input = suggestion
    elif st.session_state.current_page == "Search Documents":
        st.session_state.search_query = suggestion
    st.rerun()

# Sidebar with information (keep this)
st.sidebar.title("StudyRAG Assistant")
st.sidebar.image("https://www.svgrepo.com/show/353622/document-text.svg", width=100)
st.sidebar.markdown("---")
st.sidebar.info("""
This application uses RAG (Retrieval-Augmented Generation) to answer questions based on your documents.

📚 Upload your study materials
🔍 Search through your documents
💬 Ask questions about the content
""")

# Check API status
try:
    response = requests.get(f"{API_URL}/")
    if response.status_code == 200:
        st.sidebar.success("✅ API Connected")
    else:
        st.sidebar.error("❌ API Error")
except:
    st.sidebar.error("❌ API Not Available")

st.sidebar.markdown("---")
with st.sidebar.expander("📋 Frequently Asked Questions", expanded=False):
    for i, faq in enumerate(faq_data):
        st.markdown(f"**Q: {faq['question']}**")
        st.markdown(f"{faq['answer']}")
        if i < len(faq_data) - 1:
            st.markdown("---")
# Top Navigation Bar
nav_options = ["Chat with Documents", "Upload Documents", "Manage Documents", "Search Documents"]
cols = st.columns(len(nav_options))

with st.container():
    st.markdown('<div class="navbar">', unsafe_allow_html=True)
    for i, option in enumerate(nav_options):
        is_active = st.session_state.current_page == option
        button_type = "primary" if is_active else "secondary"
        if cols[i].button(option, key=f"nav_{i}", type=button_type, use_container_width=True):
            st.session_state.current_page = option
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Main content based on current page
if st.session_state.current_page == "Chat with Documents":
    st.title("Chat with Your Documents")
    
    # Interactive chat input with suggestions
    if 'chat_input' not in st.session_state:
        st.session_state.chat_input = ""
    
    chat_input = st.text_input(
        "Ask a question about your documents:", 
        value=st.session_state.chat_input,
        key="chat_input",
        on_change=update_search_suggestions
    )
    
    # Show suggestions as the user types
    if st.session_state.filtered_suggestions:
        st.markdown("### Suggestions")
        for suggestion in st.session_state.filtered_suggestions:
            if st.button(f"➡️ {suggestion[:80]}...", key=f"sug_{suggestion[:10]}", use_container_width=True):
                st.session_state.chat_input = suggestion
                st.rerun()
    
    # Form for submission
    with st.form("query_form", clear_on_submit=False):
        user_question = st.text_area("or type a longer question here:", 
                                     value=st.session_state.chat_input, 
                                     height=68)
        max_sources = st.slider("Maximum number of sources to return:", min_value=1, max_value=10, value=3)
        submitted = st.form_submit_button("Submit Question")
    
    if submitted and user_question:
        # Add to recent searches
        if user_question not in st.session_state.recent_searches:
            st.session_state.recent_searches.insert(0, user_question)
            if len(st.session_state.recent_searches) > 10:
                st.session_state.recent_searches.pop()
        
        with st.spinner("Generating response..."):
            try:
                payload = {
                    "question": user_question,
                    "max_sources": max_sources
                }
                
                response = requests.post(
                    f"{API_URL}/query",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.session_state.current_response = result
                    st.session_state.query_history.append({
                        "question": user_question,
                        "response": result,
                        "timestamp": time.time()
                    })
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to API: {str(e)}")
    
    # Display the current response
    if st.session_state.current_response:
        st.markdown("### Answer")
        st.write(st.session_state.current_response["answer"])
        
        st.markdown("### Sources")
        for i, source in enumerate(st.session_state.current_response["sources"], 1):
            with st.expander(f"Source {i}: {source['source']}"):
                st.markdown(f"```\n{source['content']}\n```")
    
    # Display query history
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### Previous Questions")
        
        for i, item in enumerate(reversed(st.session_state.query_history)):
            if i >= 5:  # Limit to showing the 5 most recent questions
                break
                
            with st.expander(f"Q: {item['question'][:50]}... ({format_timestamp(item['timestamp'])})"):
                st.markdown("#### Answer")
                st.write(item["response"]["answer"])
                
                st.markdown("#### Sources")
                for j, source in enumerate(item["response"]["sources"], 1):
                    st.markdown(f"**Source {j}:** {source['source']}")
                    st.text(f"{source['content'][:200]}...")

elif st.session_state.current_page == "Upload Documents":
    st.title("Upload Documents")
    
    st.markdown("""
    Upload your study materials to be processed by the RAG system. 
    Supported file types: PDF, TXT, JSON, PPT, PPTX
    """)
    
    with st.container():
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt", "json", "ppt", "pptx"])
        
        if uploaded_file:
            st.write(f"Selected file: {uploaded_file.name}")
            
            if st.button("Process Document"):
                with st.spinner("Uploading and processing document..."):
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        
                        response = requests.post(
                            f"{API_URL}/upload",
                            files=files
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"Successfully uploaded {result['filename']} and processed {result['sections_processed']} sections!")
                            # Refresh document list
                            load_documents()
                        else:
                            st.error(f"Error: {response.text}")
                    except Exception as e:
                        st.error(f"Error uploading file: {str(e)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display info about document processing
    st.info("""
    When you upload a document, the system will:
    1. Split the document into smaller chunks
    2. Generate embeddings for each chunk
    3. Store them in the vector database for future retrieval
    
    Processing time depends on the size and complexity of your document.
    """)

elif st.session_state.current_page == "Manage Documents":
    st.title("Manage Documents")
    
    # Refresh button
    if st.button("Refresh Document List"):
        load_documents()
    
    documents = load_documents()
    
    if not documents:
        st.info("No documents found. Upload some documents first.")
    else:
        st.write(f"{len(documents)} documents in the system:")
        
        for doc in documents:
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                st.write(f"**{doc['filename']}**")
            with col2:
                st.write(f"Size: {format_size(doc['size_bytes'])}")
            with col3:
                if st.button(f"Delete", key=f"delete_{doc['filename']}"):
                    delete_document(doc['filename'])

elif st.session_state.current_page == "Search Documents":
    st.title("Search Documents")
    
    st.markdown("""
    Search for relevant documents without generating an answer.
    This is useful for exploring what information is available in your documents.
    """)
    
    # Interactive search with suggestions
    search_query = st.text_input(
        "Search query:", 
        key="search_query", 
        placeholder="Enter search terms...",
        on_change=update_search_suggestions
    )
    
    # Show suggestions as the user types
    if st.session_state.filtered_suggestions:
        st.markdown("### Suggestions")
        for suggestion in st.session_state.filtered_suggestions:
            if st.button(f"➡️ {suggestion[:80]}...", key=f"search_sug_{suggestion[:10]}", use_container_width=True):
                st.session_state.search_query = suggestion
                st.rerun()
    
    col1, col2 = st.columns([3, 1])
    with col2:
        search_limit = st.number_input("Max results:", min_value=1, max_value=20, value=5)
    
    if st.button("Search", key="search_button"):
        if search_query:
            # Add to recent searches
            if search_query not in st.session_state.recent_searches:
                st.session_state.recent_searches.insert(0, search_query)
                if len(st.session_state.recent_searches) > 10:
                    st.session_state.recent_searches.pop()
                    
            with st.spinner("Searching documents..."):
                try:
                    response = requests.get(
                        f"{API_URL}/search",
                        params={"query": search_query, "limit": search_limit}
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        st.session_state.search_results = results
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error connecting to API: {str(e)}")
        else:
            st.warning("Please enter a search query")
    
    # Display search results
    if st.session_state.search_results:
        st.markdown(f"### Search Results for: '{st.session_state.search_results['query']}'")
        
        for i, result in enumerate(st.session_state.search_results['results'], 1):
            with st.expander(f"Result {i}: {result['source']}", expanded=i==1):
                st.markdown(f"```\n{result['content']}\n```")
    
    # Display recent searches
    if st.session_state.recent_searches:
        st.markdown("---")
        st.markdown("### Recent Searches")
        for i, search in enumerate(st.session_state.recent_searches):
            if st.button(f"🔄 {search}", key=f"recent_{i}", use_container_width=True):
                st.session_state.search_query = search
                st.rerun()

if __name__ == "__main__":
    pass  # Streamlit automatically runs the script