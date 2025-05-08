import requests
from bs4 import BeautifulSoup

class CustomScrapeWebsiteTool:
    def __init__(self, website_url=None):
        self.website_url = website_url
        self.name = "Website Scraper"
        self.description = "Scrapes content from a website URL"
    
    def run(self, website_url=None):
        """Scrape the content of a website."""
        url = website_url or self.website_url
        if not url:
            return "Error: No URL provided"
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
                
            # Extract text
            text = soup.get_text(separator='\n')
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        
        except Exception as e:
            return f"Error scraping website: {str(e)}"