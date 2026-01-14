import webbrowser
import wikipedia
try:
    from googleapiclient.discovery import build
except ImportError:
    build = None

from . import register_tool
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID

@register_tool("Searches Wikipedia for a summary of a topic. Good for general knowledge. Args: query (str)")
def wikipedia_search(query):
    try:
        # Set language to French for better consistency with user request
        wikipedia.set_lang("fr") 
        # Get more context (5 sentences)
        summary = wikipedia.summary(query, sentences=5)
        return summary
    except wikipedia.exceptions.DisambiguationError as e:
        return f"Ambiguous term. Options: {e.options[:5]}"
    except wikipedia.exceptions.PageError:
        return "Page not found."
    except Exception as e:
        return f"Error: {e}"

@register_tool("Searches YouTube and opens the first video. Args: query (str)")
def youtube_search(query):
    # Simple implementation: Open search query directly. 
    # To get a specific video link programmatically requires scraping or API.
    # We will open the search result page for simplicity and guaranteed success without keys.
    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Opened YouTube search for: {query}"

@register_tool("Searches Google and returns a link. Args: query (str)")
def google_search(query):
    if GOOGLE_API_KEY and GOOGLE_CSE_ID and build:
        try:
            service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
            res = service.cse().list(q=query, cx=GOOGLE_CSE_ID, num=1).execute()
            if 'items' in res:
                title = res['items'][0]['title']
                link = res['items'][0]['link']
                return f"Result: {title} - {link}"
        except Exception as e:
            return f"Google API Error: {e}"
    
    # Fallback to browser open if no key
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    webbrowser.open(url)
    return f"Opened Google search for: {query} (API key not configured)"
