import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in environment variables. Please add it to your .env file")

# Vector store configuration
CHROMA_PERSIST_DIRECTORY = "chroma_db"

# Text splitting configuration
CHUNK_SIZE = 500  # Smaller chunks for better retrieval
CHUNK_OVERLAP = 100  # Decent overlap to maintain context

# Model configuration
EMBEDDING_MODEL = "models/embedding-001"
GEMINI_MODEL = "gemini-pro"

# RAG configuration
MAX_RELEVANT_CHUNKS = 5
TEMPERATURE = 0.7 