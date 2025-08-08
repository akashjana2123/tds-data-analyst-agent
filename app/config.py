# app/config.py
import os
from dotenv import load_dotenv
import requests

load_dotenv()

AI_PROXY_URL = os.getenv("AI_PROXY_URL", "").rstrip("/")
AI_PROXY_KEY = os.getenv("AI_PROXY_KEY", "")

AI_PIPE_URL = os.getenv("AI_PIPE_URL", "").rstrip("/")
AI_PIPE_KEY = os.getenv("AI_PIPE_KEY", "")

PERPLEXITY_KEY = os.getenv("PERPLEXITY_KEY", "")

API_TIMEOUT_SECONDS = int(os.getenv("API_TIMEOUT_SECONDS", "170"))

def call_aiproxy(prompt: str, url: str = None, key: str = None, model: str = "gpt-4o-mini", extras: dict = None, timeout=30):
    """
    Generic wrapper to call a REST LLM proxy.
    By default uses AI_PROXY_URL + AI_PROXY_KEY if present, otherwise falls back to AI_PIPE_URL.
    `url` and `key` can be passed to override per-call.
    """
    endpoint = url or (AI_PROXY_URL if AI_PROXY_URL else AI_PIPE_URL)
    token = key or (AI_PROXY_KEY if AI_PROXY_KEY else AI_PIPE_KEY)
    if not endpoint or not token:
        raise RuntimeError("No AI proxy configured (set AI_PROXY_URL/AI_PROXY_KEY or AI_PIPE_URL/AI_PIPE_KEY in .env).")

    payload = {"model": model, "prompt": prompt}
    if extras:
        payload.update(extras)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()

def call_generic_rest(url: str, body: dict, token: str = None, header_name: str = "Authorization", timeout: int = 30):
    headers = {}
    if token:
        headers[header_name] = f"Bearer {token}"
    resp = requests.post(url, json=body, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()
