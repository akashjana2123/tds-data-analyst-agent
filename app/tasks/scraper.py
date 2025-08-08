# app/tasks/scraper.py
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import List, Dict

def download_html(url: str, timeout=30) -> str:
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "tds-data-agent/1.0"})
    resp.raise_for_status()
    return resp.text

def parse_wikipedia_highest_grossing(html: str) -> pd.DataFrame:
    """
    Parse the 'Highest-grossing films' table found on the provided Wikipedia page HTML.
    Returns dataframe with columns: Rank, Peak, Title, Worldwide gross, Year
    """
    soup = BeautifulSoup(html, "html.parser")
    # locate table header that contains "Highest-grossing films" or look for table with headers
    tables = soup.find_all("table", {"class": "wikitable"})
    target = None
    for t in tables:
        hdrs = [th.get_text(strip=True).lower() for th in t.find_all("th")]
        if any("worldwide gross" in h or "worldwide" in h for h in hdrs):
            target = t
            break
    if target is None:
        # fallback: choose first wikitable
        if tables:
            target = tables[0]
        else:
            raise ValueError("No table found in provided HTML")

    rows = []
    for tr in target.find_all("tr"):
        cols = tr.find_all(["td", "th"])
        if not cols:
            continue
        texts = [c.get_text(" ", strip=True) for c in cols]
        # attempt to parse rows that have at least 5 columns: Rank, Peak, Title, Worldwide gross, Year
        if len(texts) >= 5:
            rows.append(texts[:5])

    df = pd.DataFrame(rows, columns=["Rank", "Peak", "Title", "Worldwide gross", "Year"])
    # clean numeric columns
    def clean_int(x):
        try:
            return int(re.sub(r"[^\d\-]", "", x))
        except:
            return None
    def clean_money(x):
        if x is None:
            return None
        s = re.sub(r"[^\d\.]", "", x)
        try:
            return float(s)
        except:
            return None
    df["Rank"] = df["Rank"].apply(clean_int)
    df["Peak"] = df["Peak"].apply(clean_int)
    df["Year"] = df["Year"].apply(clean_int)
    df["Worldwide gross"] = df["Worldwide gross"].apply(clean_money)
    # drop rows that lack Rank or Title
    df = df.dropna(subset=["Rank", "Title"])
    df = df.reset_index(drop=True)
    return df
