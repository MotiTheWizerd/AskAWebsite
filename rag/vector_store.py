from typing import List, Optional, Tuple
import chromadb
from chromadb.config import Settings
from langchain.schema import Document
import google.generativeai as genai
from . import config
import uuid
import time
import os

class VectorStore:
    def __init__(self):
        # Ensure the persistence directory exists
        os.makedirs(config.CHROMA_PERSIST_DIRECTORY, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_PERSIST_DIRECTORY,
            settings=Settings(
                anonymized_telemetry=False,
                is_persistent=True
            )
        )
        
        # Try to get existing collection or create new one
        try:
            self.collection = self.client.get_collection("documents")
            doc_count = self.count_documents()
            print(f"Loaded existing collection with {doc_count} documents")
            if doc_count > 0:
                # Print a sample document
                sample = self.collection.get(limit=1)
                print("\nSample document content:")
                print(f"Content: {sample['documents'][0][:200]}...")
                print(f"Metadata: {sample['metadatas'][0]}")
        except:
            print("Creating new collection 'documents'")
            self.collection = self.client.create_collection("documents")
            
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(config.GEMINI_MODEL)
    
    def count_documents(self) -> int:
        """
        Get the number of documents in the collection
        """
        try:
            return self.collection.count()
        except Exception:
            return 0
    
    def clear_database(self):
        """
        Clear all documents from the database
        """
        try:
            self.client.delete_collection("documents")
        except ValueError:
            pass  # Collection doesn't exist
        self.collection = self.client.create_collection("documents")
        print("Database cleared")
    
    def _generate_unique_id(self) -> str:
        """
        Generate a unique ID for a document using UUID and timestamp
        """
        timestamp = int(time.time() * 1000)  # millisecond timestamp
        unique_id = f"{timestamp}_{str(uuid.uuid4())[:8]}"
        return unique_id
    
    def add_documents(self, documents: List[Document]):
        """
        Add documents to the vector store
        """
        # Prepare batches of documents
        doc_contents = []
        doc_embeddings = []
        doc_metadatas = []
        doc_ids = []
        
        for doc in documents:
            embedding = self._get_simple_embedding(doc.page_content)
            doc_contents.append(doc.page_content)
            doc_embeddings.append(embedding)
            doc_metadatas.append(doc.metadata)
            doc_ids.append(self._generate_unique_id())
        
        # Add documents in a single batch
        if doc_contents:
            try:
                self.collection.add(
                    documents=doc_contents,
                    embeddings=doc_embeddings,
                    metadatas=doc_metadatas,
                    ids=doc_ids
                )
                print(f"Successfully added {len(doc_contents)} documents to the collection")
            except Exception as e:
                print(f"Error adding documents to collection: {str(e)}")
    
    def _get_simple_embedding(self, text: str, vector_size: int = 384) -> List[float]:
        """
        Create a simple deterministic embedding from text.
        Using a smaller vector size (384) for better similarity matching.
        """
        import hashlib
        import numpy as np
        
        # Create a deterministic hash of the text
        text_hash = hashlib.sha256(text.encode()).hexdigest()
        
        # Use the hash to seed numpy's random number generator
        np.random.seed(int(text_hash[:8], 16))
        
        # Generate a random vector
        embedding = np.random.uniform(-1, 1, vector_size)
        
        # Normalize the vector
        embedding = embedding / np.linalg.norm(embedding)
        
        return embedding.tolist()
    
    def similarity_search(self, query: str, k: Optional[int] = None) -> List[Document]:
        """
        Search for similar documents using the query
        """
        if k is None:
            k = config.MAX_RELEVANT_CHUNKS
            
        if self.count_documents() == 0:
            print("Warning: No documents in the database")
            return []
            
        try:
            # Get all documents first to inspect what we have
            all_docs = self.collection.get()
            print(f"\nTotal documents in database: {len(all_docs['documents'])}")
            
            # Perform the search
            query_embedding = self._get_simple_embedding(query)
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=min(k, self.count_documents())
            )
            
            documents = []
            if results['documents'] and len(results['documents'][0]) > 0:
                for i in range(len(results['documents'][0])):
                    doc = Document(
                        page_content=results['documents'][0][i],
                        metadata=results['metadatas'][0][i]
                    )
                    documents.append(doc)
                    
                # Print debug information
                print(f"\nFound {len(documents)} relevant documents:")
                for i, doc in enumerate(documents, 1):
                    print(f"\nDocument {i}:")
                    print(f"URL: {doc.metadata.get('url', 'unknown')}")
                    print(f"Content length: {len(doc.page_content)} characters")
                    print(f"Content preview: {doc.page_content[:500]}...")
            else:
                print("\nNo relevant documents found for the query.")
                
            return documents
        except Exception as e:
            print(f"Error during similarity search: {str(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return [] 