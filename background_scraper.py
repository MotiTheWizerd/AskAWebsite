from multiprocessing import Process, Queue
import asyncio
from scraper_methods import start_scraping_website
from typing import Dict, Any

def scraper_process(url: str, status_queue: Queue):
    """Background process to handle website scraping."""
    try:
        # Run the async scraping in a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Execute scraping
        status_queue.put({"status": "running", "message": f"Started scraping {url}"})
        result = loop.run_until_complete(start_scraping_website(url))
        
        # Send final status
        if result:
            status_queue.put({"status": "completed", "message": "Scraping completed successfully"})
        else:
            status_queue.put({"status": "failed", "message": "Scraping failed"})
            
    except Exception as e:
        status_queue.put({"status": "error", "message": str(e)})
    finally:
        loop.close()

def start_background_scraping(url: str) -> Queue:
    """Start the scraping process in the background."""
    status_queue = Queue()
    process = Process(target=scraper_process, args=(url, status_queue))
    process.start()
    return status_queue 