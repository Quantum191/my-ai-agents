import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger("WebScraper")

def scrape_url(url):
    """Scrapes the main text content from a given URL."""
    if not url:
        return "Error: No URL provided by the AI."
    
    # Clean up the URL if the LLM accidentally adds JSON quotes to the string
    url = str(url).strip("\"'")
    
    if not url.startswith('http'):
        url = 'https://' + url

    try:
        # We use a standard User-Agent so websites don't instantly block our bot
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) DEV-01 Agent'}
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Rip out all the junk (scripts, styles, headers, footers)
        for junk in soup(["script", "style", "nav", "footer", "header", "aside"]):
            junk.extract()
            
        # Extract the clean, readable text
        text = soup.get_text(separator=' ', strip=True)
        
        # --- CRITICAL SAFEGUARD ---
        # Truncate to 3000 characters so we don't crash Ollama's memory window
        max_chars = 3000 
        if len(text) > max_chars:
            return f"SUCCESS. Text extracted (Truncated to {max_chars} chars):\n\n{text[:max_chars]}...\n\n[CONTENT TRUNCATED]"
        
        return f"SUCCESS. Text extracted:\n\n{text}"
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Scraping failed for {url}: {e}")
        return f"Network Error: Could not fetch {url}. Details: {str(e)}"
    except Exception as e:
        logger.error(f"Parsing failed: {e}")
        return f"Parsing Error: {str(e)}"
