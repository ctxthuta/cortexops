"""Technical Web & Blog Research Tools."""

import urllib.request
import urllib.parse
import ipaddress
from bs4 import BeautifulSoup
import re

def search_web(query: str, max_results: int = 5) -> str:
    """Searches the web for technical documentation, engineering blogs, and GitHub repositories.
    
    Args:
        query: Technical search query (e.g. 'go goroutine worker pool graceful shutdown pattern').
        max_results: Max search results to retrieve (default: 5).
        
    Returns:
        Summary of relevant links, titles, and snippets.
    """
    clean_query = query.strip()
    encoded = urllib.parse.quote(clean_query)
    # Use DuckDuckGo HTML search for direct, dependency-free technical search
    url = f"https://html.duckduckgo.com/html/?q={encoded}"
    
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
        soup = BeautifulSoup(html, "html.parser")
        results = []
        for result in soup.find_all("div", class_="result__body")[:max_results]:
            title_tag = result.find("a", class_="result__url")
            snippet_tag = result.find("a", class_="result__snippet")
            
            if title_tag:
                raw_url = title_tag.get("href", "")
                # Clean URL redirect if present
                if "uddg=" in raw_url:
                    parsed_url = urllib.parse.unquote(raw_url.split("uddg=")[1].split("&")[0])
                else:
                    parsed_url = raw_url
                title = title_tag.get_text(strip=True)
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                results.append(f"Title: {title}\nURL: {parsed_url}\nSnippet: {snippet}\n")
                
        if not results:
            return f"No web results found for '{clean_query}'."
            
        return "\n".join(results)
    except Exception as e:
        return f"Error executing web search: {str(e)}"

def read_web_page(url: str, max_chars: int = 8000) -> str:
    """Fetches a web page or technical documentation and converts it into clean readable text.
    
    Args:
        url: The web URL to inspect.
        max_chars: Character limit to avoid context blowout (default: 8000).
        
    Returns:
        Cleaned plain text of the article/documentation.
    """
    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme not in ("http", "https"):
        return f"ERROR: Blocked unsupported scheme '{parsed.scheme}'. Only HTTP and HTTPS are permitted."

    hostname = parsed.hostname or ""
    if hostname in ("localhost", "127.0.0.1", "::1", "169.254.169.254"):
        return "ERROR: Access to loopback or cloud metadata services is prohibited."

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return f"ERROR: Access to private network destination '{hostname}' is prohibited."
    except ValueError:
        pass

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.extract()
            
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        clean_text = "\n".join(lines)
        
        if len(clean_text) > max_chars:
            return clean_text[:max_chars] + f"\n... [Truncated to {max_chars} chars]"
        return clean_text
    except Exception as e:
        return f"Error reading web page {url}: {str(e)}"
