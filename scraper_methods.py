from crawl4ai import AsyncWebCrawler
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
from typing import List, Dict, Any
import xml.etree.ElementTree as ET
import aiohttp
from urllib.parse import urlparse

async def extract_urls_from_sitemap(
    sitemap_url: str,
    include_paths: List[str] = ['/api/', '/examples/', '/guide/']
) -> List[Dict[str, Any]]:
    """
    Extract structured data from a sitemap including URLs, types, and images.
    
    Args:
        sitemap_url: URL of the sitemap to process
        include_paths: List of paths to include (e.g., ['/api/', '/guide/'])
        
    Returns:
        List of dictionaries containing:
        - url: The page URL
        - type: Content type (api, example, guide)
        - path: The relative path
        - source: Source of the URL (sitemap)
        - images: List of image dictionaries with url, alt, and title
    """
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(sitemap_url) as response:
                if response.status != 200:
                    print(f"Failed to fetch sitemap: HTTP {response.status}")
                    return []
                    
                sitemap_content = await response.text()
                root = ET.fromstring(sitemap_content)
                
                # Register XML namespaces
                namespaces = {
                    'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9',
                    'image': 'http://www.google.com/schemas/sitemap-image/1.1'
                }
                
                # Extract URLs with metadata
                structured_urls = []
                
                # Look for URLs in sitemap
                for url_elem in root.findall('.//sm:url', namespaces):
                    # Get the main URL
                    loc_elem = url_elem.find('sm:loc', namespaces)
                    if loc_elem is None or not loc_elem.text:
                        continue
                        
                    url = loc_elem.text
                    
                    # Skip sitemap XML files
                    if url.endswith('sitemap.xml'):
                        continue
                    
                    # Check if URL matches any of the include paths
                    path = urlparse(url).path
                    url_type = None
                    for include_path in include_paths:
                        if include_path.strip('/') in path:
                            url_type = include_path.strip('/')
                            break
                    
                    if url_type is None:
                        continue  # Skip URLs that don't match include paths
                    
                    # Extract images for this URL
                    images = []
                    for img_elem in url_elem.findall('.//image:image', namespaces):
                        image_data = {}
                        
                        # Get image URL
                        img_loc = img_elem.find('image:loc', namespaces)
                        if img_loc is not None and img_loc.text:
                            image_data['url'] = img_loc.text
                            
                            # Get optional image metadata
                            img_title = img_elem.find('image:title', namespaces)
                            if img_title is not None and img_title.text:
                                image_data['title'] = img_title.text
                                
                            img_caption = img_elem.find('image:caption', namespaces)
                            if img_caption is not None and img_caption.text:
                                image_data['alt'] = img_caption.text
                                
                            images.append(image_data)
                    
                    # Create structured data for this URL
                    structured_urls.append({
                        'url': url,
                        'type': url_type,
                        'path': path,
                        'source': 'sitemap',
                        'images': images
                    })
                
                print(f"Found {len(structured_urls)} matching URLs in sitemap")
                return structured_urls
                
        except Exception as e:
            print(f"Error processing sitemap: {str(e)}")
            return []

async def crawl_sitemap(sitemap_url: str) -> List[Dict[str, Any]]:
    """
    Crawl a website's sitemap and extract content from each URL.
    """
    results = []
    
    # First extract all URLs from the sitemap with metadata
    structured_urls = await extract_urls_from_sitemap(sitemap_url)
    print(f"Found {len(structured_urls)} documentation URLs in sitemap")
    
    if not structured_urls:
        return results
    
    # Initialize crawler with configs
    browser_config = BrowserConfig(verbose=True)
    run_config = CrawlerRunConfig(
        word_count_threshold=10,
        remove_overlay_elements=True
    )
    
    # Crawl each URL
    async with AsyncWebCrawler(config=browser_config) as crawler:
        for url_data in structured_urls:
            try:
                result = await crawler.arun(url=url_data['url'], config=run_config)
                if result.success and result.markdown:
                    # Print detailed content preview for debugging
                    print(f"\nSuccessfully crawled: {url_data['url']}")
                    print(f"Content type: {url_data['type']}")
                    print(f"Content length: {len(result.markdown)} characters")
                    print("Content preview:")
                    print("-" * 50)
                    print(result.markdown[:500])
                    print("-" * 50)
                    
                    results.append({
                        **url_data,  # Include all metadata from structured_urls
                        "content": result.markdown,
                        "status": "success"
                    })
                else:
                    print(f"Failed to crawl {url_data['url']}: {result.error_message if result.error_message else 'No content extracted'}")
                    results.append({
                        **url_data,
                        "content": None,
                        "status": "failed",
                        "error": result.error_message if result.error_message else "No content extracted"
                    })
            except Exception as e:
                print(f"Error crawling {url_data['url']}: {str(e)}")
                results.append({
                    **url_data,
                    "content": None,
                    "status": "error",
                    "error": str(e)
                })
                
    return results 