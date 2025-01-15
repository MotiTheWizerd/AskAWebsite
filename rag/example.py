from langchain.schema import Document
from rag_engine import RAGEngine

def main():
    # Initialize the RAG engine
    rag = RAGEngine()
    
    # Example documents
    documents = [
        Document(
            page_content="The Python programming language was created by Guido van Rossum and was first released in 1991.",
            metadata={"source": "python_history.txt"}
        ),
        Document(
            page_content="Python is known for its simple syntax and readability. It follows the philosophy of 'explicit is better than implicit'.",
            metadata={"source": "python_features.txt"}
        )
    ]
    
    # Add documents to the RAG system
    rag.add_documents(documents)
    
    # Example queries
    queries = [
        "Who created Python?",
        "What is Python known for?",
        "When was Java created?"  # This should return "not enough information"
    ]
    
    # Test the RAG system
    for query in queries:
        print(f"\nQuestion: {query}")
        answer = rag.query(query)
        print(f"Answer: {answer}\n")
        print("-" * 50)

if __name__ == "__main__":
    main() 