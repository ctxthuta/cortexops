"""arXiv Academic Research Tools for R&D Engineer."""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import os
import tempfile
import io
import pypdf

def search_arxiv(query: str, max_results: int = 5) -> str:
    """Searches the arXiv scientific preprint repository for academic papers.
    
    Args:
        query: Academic search keywords (e.g., 'streaming anomaly detection metric telemetry').
        max_results: Maximum number of papers to retrieve (default: 5).
        
    Returns:
        Structured summary containing Paper Title, arXiv ID, Authors, Published Date,
        and the full Abstract.
    """
    clean_query = query.strip()
    encoded = urllib.parse.quote(clean_query)
    url = f"http://export.arxiv.org/api/query?search_query=all:{encoded}&start=0&max_results={max_results}&sortBy=relevance&sortOrder=descending"
    
    req = urllib.request.Request(url, headers={"User-Agent": "Thea-Engineering-Team-Agent/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            xml_data = response.read()
            
        root = ET.fromstring(xml_data)
        namespace = {"atom": "http://www.w3.org/2005/Atom"}
        entries = root.findall("atom:entry", namespace)
        
        if not entries:
            return f"No papers found on arXiv matching query: '{clean_query}'"
            
        results = [f"Found {len(entries)} arXiv papers for query: '{clean_query}'\n"]
        for i, entry in enumerate(entries, 1):
            title = entry.find("atom:title", namespace).text.strip().replace("\n", " ")
            summary = entry.find("atom:summary", namespace).text.strip().replace("\n", " ")
            published = entry.find("atom:published", namespace).text[:10]
            id_url = entry.find("atom:id", namespace).text.strip()
            arxiv_id = id_url.split("/abs/")[-1]
            
            authors = [a.find("atom:name", namespace).text for a in entry.findall("atom:author", namespace)]
            authors_str = ", ".join(authors[:4]) + (" et al." if len(authors) > 4 else "")
            
            results.append(
                f"[{i}] {title}\n"
                f"    arXiv ID: {arxiv_id}\n"
                f"    Authors: {authors_str} ({published})\n"
                f"    PDF URL: https://arxiv.org/pdf/{arxiv_id}.pdf\n"
                f"    Abstract: {summary}\n"
            )
            
        return "\n".join(results)
    except Exception as e:
        return f"Error searching arXiv: {str(e)}"

def read_arxiv_paper_pdf(arxiv_id: str, max_pages: int = 5) -> str:
    """Downloads an arXiv paper PDF and extracts clean text from the first several pages.
    
    Args:
        arxiv_id: The arXiv identifier (e.g., '2305.12345' or '1706.03762').
        max_pages: Number of pages to extract (default: 5, focuses on Abstract, Intro, Methodology).
        
    Returns:
        Extracted plain text of the paper for deep algorithmic analysis.
    """
    clean_id = arxiv_id.strip().replace("abs/", "").replace(".pdf", "")
    pdf_url = f"https://arxiv.org/pdf/{clean_id}.pdf"
    
    req = urllib.request.Request(pdf_url, headers={"User-Agent": "Thea-Engineering-Team-Agent/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=25) as response:
            pdf_bytes = response.read()
            
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        num_pages = len(reader.pages)
        pages_to_read = min(max_pages, num_pages)
        
        extracted = [f"=== arXiv:{clean_id} (Extracted {pages_to_read} of {num_pages} pages) ===\n"]
        for p in range(pages_to_read):
            text = reader.pages[p].extract_text()
            extracted.append(f"--- PAGE {p+1} ---\n{text}\n")
            
        return "\n".join(extracted)
    except Exception as e:
        return f"Error downloading/parsing arXiv PDF {clean_id}: {str(e)}"
