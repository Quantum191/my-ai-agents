import os
from contextlib import redirect_stderr
from duckduckgo_search import DDGS

def search_web(query):
    """Searches the web using DuckDuckGo, safely muffling library-level stderr."""
    try:
        # Antigravity Fix: Use a context manager to redirect stderr to /dev/null
        # This only 'hides' errors during the search itself, keeping your CLI clean.
        with open(os.devnull, 'w') as f, redirect_stderr(f):
            results = DDGS().text(query, max_results=3)
            
        if not results:
            return "No results found."
            
        summary = "\n".join([f"- {r['title']}: {r['href']}" for r in results])
        return summary
    except Exception as e:
        return f"Search Error: {str(e)}"

if __name__ == "__main__":
    # Quick local test
    print(search_web("Arch Linux news"))
