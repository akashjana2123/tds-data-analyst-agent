# app/tasks/parser.py
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse

def extract_first_url(text: str) -> Optional[str]:
    urls = re.findall(r"https?://[^\s\)]+", text)
    return urls[0] if urls else None

def detect_task(text: str) -> Dict[str, Any]:
    """
    Very small rule-based task detector. Returns a dict describing the action.
    """
    text_low = text.lower()
    res = {"type": "generic", "url": None}
    url = extract_first_url(text)
    if url:
        res["url"] = url
    # simple patterns
    if "wikipedia" in text_low or (url and "wikipedia.org" in url):
        res["type"] = "wikipedia_table"
    elif "parquet" in text_low or "duckdb" in text_low or "s3://" in text_low:
        res["type"] = "duckdb_parquet"
    else:
        # if mentions "scrape" and "list of highest-grossing films" -> wiki
        if "highest-grossing films" in text_low or "highest grossing films" in text_low:
            res["type"] = "wikipedia_table"
    return res
