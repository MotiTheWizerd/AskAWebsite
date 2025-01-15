"""
Crawler module for handling web scraping using Crawl4AI.
Implements AsyncWebCrawler with configurable settings.
"""
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig, CacheMode

class AsyncCrawlerManager:
    """Manages asynchronous web crawling operations using Crawl4AI."""
    
    def __init__(self):
        """Initialize crawler with default configurations."""
        self.browser_config = BrowserConfig(
            verbose=True,
            headless=True
        )
        
        self.run_config = CrawlerRunConfig(
            word_count_threshold=10,
            excluded_tags=['nav', 'footer'],
            exclude_external_links=True,
            cache_mode=CacheMode.ENABLED
        )
    
    async def crawl(self, url: str):
        """
        Crawl a given URL and return the results.
        
        Args:
            url (str): The URL to crawl
            
        Returns:
            CrawlResult: The result of the crawling operation
        """
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(
                url=url,
                config=self.run_config
            )
            return result 