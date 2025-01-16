import asyncio
from scraper_methods import crawl_sitemap
from rag.rag_engine import RAGEngine
from typing import List

def query_rag_system(rag: RAGEngine, queries: List[str]) -> None:
    """
    Query the RAG system with a list of questions.
    
    Args:
        rag: Instance of RAGEngine to query
        queries: List of questions to ask
    """
    print("\nQuerying RAG system:")
    print("=" * 50)
    
    for query in queries:
        print(f"\nQuestion: {query}")
        answer = rag.query(query)
        print(f"Answer: {answer}")
        print("-" * 50)

async def main():
    pass  # New implementation will go here

if __name__ == "__main__":
    asyncio.run(main())

#     async def example_usage():
    # Initialize the RAG engine
    # rag = RAGEngine()
    # # Check if we need to populate the database
    # if rag.vector_store.count_documents() == 0:
    #     print("Database is empty. Scraping and populating with content...")
    #     # Scrape content
    #     scraped_results = await crawl_sitemap("https://ai.pydantic.dev/sitemap.xml")
    #     # Populate database with scraped content
    #     rag.populate_from_scraped_results(scraped_results, clear_db=True)
    # else:
    #     print(f"Using existing database with {rag.vector_store.count_documents()} documents")
    
    # # Test the RAG system with AI-specific queries
    # test_queries = [
    #     "How can I use Pydantic with the Gemini API?",
    #     "What are the main features of Pydantic AI?", 
    #     "How do I validate AI model responses with Pydantic?",
    #     "What is the AsyncAnthropic client in Pydantic AI?",
    #     "How do I create an AI agent with Pydantic?"
    # ]
    # query_rag_system(rag, test_queries)
