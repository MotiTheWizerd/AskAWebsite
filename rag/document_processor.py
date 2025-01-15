from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import google.generativeai as genai
from . import config

class DocumentProcessor:
    def __init__(self):
        genai.configure(api_key=config.GEMINI_API_KEY)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", ", ", " ", ""]
        )
        
    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content
        """
        # Remove multiple newlines
        text = '\n'.join(line.strip() for line in text.split('\n') if line.strip())
        # Remove multiple spaces
        text = ' '.join(text.split())
        return text
        
    def process_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Document]:
        """
        Process raw text into chunks suitable for embedding
        """
        if metadata is None:
            metadata = {}
            
        # Clean the text
        cleaned_text = self.clean_text(text)
        
        # Create a document
        doc = Document(page_content=cleaned_text, metadata=metadata)
        
        # Split the document into chunks
        chunks = self.text_splitter.split_documents([doc])
        
        print(f"Split document into {len(chunks)} chunks")
        for i, chunk in enumerate(chunks, 1):
            print(f"\nChunk {i} length: {len(chunk.page_content)} characters")
            print(f"Preview: {chunk.page_content[:200]}...")
        
        return chunks
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process multiple documents into chunks
        """
        all_chunks = []
        for doc in documents:
            # Clean the text
            doc.page_content = self.clean_text(doc.page_content)
            # Split into chunks
            chunks = self.text_splitter.split_documents([doc])
            all_chunks.extend(chunks)
        return all_chunks 