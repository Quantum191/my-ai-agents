import os
import sys

# Muzzle any remaining warnings just in case
stderr = sys.stderr
sys.stderr = open(os.devnull, 'w')

try:
    # WE USE THE NEW LIBRARY NAME HERE!
    from ddgs import DDGS
finally:
    sys.stderr = stderr

def search_web(query, max_results=3):
    """Clean search using the newly installed ddgs library."""
    try:
        with DDGS() as ddgs:
            results = [r for r in ddgs.text(query, max_results=max_results)]
            
        if not results:
            return "No search results found."
        
        output = []
        for res in results:
            title = res.get('title', 'N/A')
            body = res.get('body', 'N/A')
            output.append(f"TITLE: {title}\nINFO: {body}\n")
            
        return "\n".join(output)
    
    except Exception as e:
        return f"Search failed: {str(e)}"

if __name__ == "__main__":
    # Test print
    print(search_web("Tokyo Weather"))
