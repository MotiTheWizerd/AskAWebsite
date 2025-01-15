from typing import List, Optional, Dict, Any
import google.generativeai as genai
from langchain.schema import Document
from .document_processor import DocumentProcessor
from .vector_store import VectorStore
from . import config

class RAGEngine:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
        self.document_processor = DocumentProcessor()
        self.vector_store = VectorStore()
        
    def add_documents(self, documents: List[Document]):
        """
        Process and add documents to the vector store
        """
        chunks = self.document_processor.process_documents(documents)
        self.vector_store.add_documents(chunks)
        
    def add_text(self, text: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Process and add raw text to the vector store
        """
        chunks = self.document_processor.process_text(text, metadata)
        self.vector_store.add_documents(chunks)
        
    def populate_from_scraped_results(self, scraped_results: List[Dict[str, Any]], clear_db: bool = False) -> None:
        """
        Populate the database from scraped results.
        
        Args:
            scraped_results: List of dictionaries containing scraped content and metadata
            clear_db: Whether to clear the database before adding new documents
        """
        if clear_db:
            self.vector_store.clear_database()
            print("Cleared existing database")
        
        successful_docs = 0
        for result in scraped_results:
            if result['status'] == 'success' and result['content']:
                # Convert images list to a string representation for metadata
                images_str = ';'.join(
                    f"{img.get('url', '')}|{img.get('title', '')}|{img.get('alt', '')}"
                    for img in result['images']
                ) if result['images'] else ''
                
                # Create a document with metadata that ChromaDB can handle
                doc = Document(
                    page_content=result['content'],
                    metadata={
                        "url": result['url'],
                        "type": result['type'],
                        "path": result['path'],
                        "source": result['source'],
                        "images": images_str  # Store images as a delimited string
                    }
                )
                
                # Add the document to the vector store
                self.add_documents([doc])
                successful_docs += 1
                
        print(f"\nSuccessfully added {successful_docs} documents to the database")
        
    def query(self, query: str) -> str:
        """
        Execute a RAG query
        """
        # Retrieve relevant documents
        relevant_docs = self.vector_store.similarity_search(query)
        
        if not relevant_docs:
            return "I don't have enough information to answer that question."
        
        # Construct the prompt with context
        context_parts = []
        for doc in relevant_docs:
            context_parts.append(
                f"Source ({doc.metadata.get('url', 'unknown')}):\n{doc.page_content}"
            )
        
        context = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""You are a helpful AI assistant with access to documentation about Pydantic and related topics. 
Your task is to answer the question based on the provided documentation excerpts.

Important instructions:
1. Base your answer ONLY on the provided documentation
2. If the documentation doesn't fully answer the question, explain what you can determine and what's missing
3. If you need to make assumptions, state them explicitly
4. Use specific examples from the documentation when possible

Documentation excerpts:
{context}

Question: {query}

Please provide a clear, accurate answer based on the documentation above. If the documentation doesn't contain enough information to fully answer the question, explain what you can determine and what information is missing."""
        
        try:
            # Generate response using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more focused responses
                    candidate_count=1,
                    max_output_tokens=1024,
                )
            )
            return response.text
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I encountered an error while generating the response. Please try again." 