import requests
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from . import register_tool

@register_tool("Performs a web search (DuckDuckGo) and returns top results. Args: query (str)")
def search_web(query):
    try:
        results = []
        with DDGS() as ddgs:
            # text search
            # max_results controls how many items we get
            count = 0
            for r in ddgs.text(query):
                count += 1
                results.append(f"Title: {r['title']}\nURL: {r['href']}\nDescription: {r['body']}\n")
                if count >= 5:
                    break
        
        if not results:
            return "No results found."
        return "\n---\n".join(results)
    except Exception as e:
        return f"Error searching web: {e}"

@register_tool("Visits a webpage and extracts the main text content. Args: url (str)")
def visit_page(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit length to avoid context overflow (approx 4000 chars)
        return text[:4000] + "\n...(content truncated)..."
    except Exception as e:
        return f"Error visiting page: {e}"
