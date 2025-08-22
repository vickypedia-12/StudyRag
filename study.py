from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.docstore.document import Document
import re
import os
from typing import List, Dict
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader,UnstructuredPowerPointLoader ,TextLoader
import json

load_dotenv()

class StudyDocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1024, 
            chunk_overlap=200, 
            add_start_index=True
        )
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )
        self.chroma_persist_dir = "chroma_db_study"
        self.vectorstore = None
        self.initialize_vectorstore()

    def initialize_vectorstore(self):
        if os.path.exists(self.chroma_persist_dir):
            self.vectorstore = Chroma(
                persist_directory=self.chroma_persist_dir,
                embedding_function=self.embeddings
            )
        else:
            self.vectorstore = Chroma(
                persist_directory=self.chroma_persist_dir,
                embedding_function=self.embeddings
            )

    def process_document(self, input_file: str):
        try:
            documents = []
            file_extension = os.path.splitext(input_file)[1].lower()
            
            # Handle different file types
            if file_extension == '.pdf':
                loader = PyPDFLoader(input_file)
                documents.extend(loader.load())

            elif file_extension in ['.ppt', '.pptx']:
                loader = UnstructuredPowerPointLoader(input_file)
                documents.extend(loader.load())
            elif file_extension == '.txt':
                loader = TextLoader(input_file)
                documents.extend(loader.load())
            elif file_extension == '.json':
                with open(input_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        for key, value in data.items():
                            if isinstance(value, str):
                                documents.append(Document(
                                    page_content=value,
                                    metadata={"source": input_file, "key": key}
                                ))
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, str):
                                documents.append(Document(
                                    page_content=item,
                                    metadata={"source": input_file}
                                ))
            
            if not documents:
                print(f"No documents loaded from {input_file}")
                return
            
            # Split documents
            texts = self.text_splitter.split_documents(documents)
            
            # Add to vectorstore
            self.vectorstore.add_documents(texts)
            
            print(f"Processed {len(texts)} sections from {input_file}")
            
        except Exception as e:
            print(f"Error processing document: {e}")
            raise


class StudyRAG:
    def __init__(self):
        self.chroma_persist_dir = "chroma_db_study"
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.environ["GOOGLE_API_KEY"]
        )
        self.vectorstore = None
        self.initialize_vectorstore()
        
    def initialize_vectorstore(self):
        if os.path.exists(self.chroma_persist_dir):
            self.vectorstore = Chroma(
                persist_directory=self.chroma_persist_dir,
                embedding_function=self.embeddings
            )
        else:
            self.vectorstore = Chroma(
                persist_directory=self.chroma_persist_dir,
                embedding_function=self.embeddings
            )

    def search_documents(self, query: str, k: int = 3):
        """Search for relevant documents and return them with their sources"""
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": k}
        )
        
        docs = retriever.invoke(query)
        results = []
        
        for doc in docs:
            source = doc.metadata.get("source", "Unknown source")
            page = doc.metadata.get("page", "")
            if page:
                source = f"{source} (page {page})"
            
            results.append({
                "content": doc.page_content,
                "source": source
            })
        
        return results

    def get_response_with_sources(self, question: str) -> Dict:
        """Get AI response along with source documents"""
        try:
            # Search for relevant documents
            docs = self.search_documents(question)
            
            retriever = self.vectorstore.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 3}
            )

            # Extract document content for the prompt
            doc_contents = "\n\n".join([f"Document from {doc['source']}:\n{doc['content']}" for doc in docs])
            
            model = ChatGoogleGenerativeAI(
                model="gemini-1.5-pro", 
                temperature=0.3,
                google_api_key=os.environ["GOOGLE_API_KEY"]
            )
            
            template = """
            You are a helpful study assistant. Answer the following question based on the provided documents.
            
            REFERENCE DOCUMENTS:
            {context}
            
            QUESTION: {query}
            
            Provide a comprehensive but concise answer. Only use information from the provided documents.
            Do not include 'Document from' or other reference markers in your answer.
            """
            
            prompt = PromptTemplate.from_template(template)
            
            def format_docs(docs):
                return "\n\n".join(doc.page_content for doc in docs)
            
            rag_chain = (
                {
                    "context": lambda x: format_docs(retriever.invoke(x["query"])),
                    "query": RunnablePassthrough()
                }
                | prompt
                | model
                | StrOutputParser()
            )
            
            response = rag_chain.invoke({"query": question})
            
            # Return both the answer and source documents
            return {
                "answer": response,
                "sources": docs
            }   
            
        except Exception as e:
            return {
                "answer": f"Error: {str(e)}",
                "sources": []
            }


def process_files(rag_processor, directory="study_materials"):
    """Process all files in the given directory"""
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"Created directory {directory}, please add your study materials there.")
        return
        
    for filename in os.listdir(directory):
        if filename.endswith(('.pdf', '.txt', '.json', '.ppt', '.pptx')):
            file_path = os.path.join(directory, filename)
            print(f"Processing {file_path}...")
            rag_processor.process_document(file_path)


def format_sources(sources):
    """Format source documents for display"""
    result = "\nSOURCES:\n"
    for i, doc in enumerate(sources, 1):
        result += f"{i}. From {doc['source']}:\n"
        result += f"   {doc['content'][:200]}{'...' if len(doc['content']) > 200 else ''}\n\n"
    return result


def main():
    print("Initializing Study RAG Application...")
    processor = StudyDocumentProcessor()
    rag = StudyRAG()
    
    # Process documents if needed
    if not os.path.exists("chroma_db_study") or not os.listdir("chroma_db_study"):
        print("No existing database found. Processing documents...")
        process_files(processor)
    
    print("\nStudy Assistant Ready!")
    
    while True:
        question = input("\nQuestion (type 'exit' to quit): ")
        if question.lower() in ['exit', 'quit']:
            break
        
        print("\nSearching knowledge base...")
        result = rag.get_response_with_sources(question)
        
        print("\n----- ANSWER -----")
        print(result["answer"])
        print("\n----- SOURCES -----")
        for i, source in enumerate(result["sources"], 1):
            print(f"{i}. From {source['source']}:")
            print(f"   {source['content'][:100]}...")
            print()


if __name__ == "__main__":
    main()