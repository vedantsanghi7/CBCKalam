import os
import yaml
import json
import hashlib
import httpx
from datetime import datetime
import asyncio

CACHE_DIR = os.path.join(os.path.dirname(__file__), "_cache")
SOURCES_FILE = os.path.join(os.path.dirname(__file__), "sources.yaml")

os.makedirs(CACHE_DIR, exist_ok=True)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10._15_7) Chrome/122.0.0.0 Safari/537.36"

async def fetch_url(client, url, scheme_id, idx):
    url_hash = hashlib.md5(url.encode()).hexdigest()
    
    # Try to guess extension
    ext = ".html"
    if url.lower().endswith(".pdf"):
        ext = ".pdf"
    
    out_file = os.path.join(CACHE_DIR, f"{scheme_id}_{url_hash}{ext}")
    meta_file = os.path.join(CACHE_DIR, f"{scheme_id}_{url_hash}.meta.json")
    
    # Cache hit
    if os.path.exists(out_file) and os.path.exists(meta_file):
        print(f"[{scheme_id}] CACHE HIT: {url}")
        return out_file
        
    print(f"[{scheme_id}] FETCHING: {url}")
    try:
        response = await client.get(url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
        content = response.content
        
        # If response was actually PDF despite no extension
        if response.headers.get("content-type", "").lower().startswith("application/pdf"):
            ext = ".pdf"
            out_file = os.path.join(CACHE_DIR, f"{scheme_id}_{url_hash}{ext}")
            
        with open(out_file, "wb") as f:
            f.write(content)
            
        with open(meta_file, "w") as f:
            json.dump({
                "url": url,
                "fetched_on": datetime.now().isoformat(),
                "sha256": hashlib.sha256(content).hexdigest(),
                "http_status": response.status_code
            }, f, indent=2)
            
        return out_file
    except Exception as e:
        print(f"[{scheme_id}] ERROR ({url}): {e}")
        return None

async def main():
    if not os.path.exists(SOURCES_FILE):
        print("sources.yaml not found!")
        return

    with open(SOURCES_FILE, "r") as f:
        sources = yaml.safe_load(f)

    async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, verify=False) as client:
        # Sequential to avoid aggressive throttling
        for scheme_id, data in sources.items():
            primary_urls = data.get("primary", [])
            for i, p in enumerate(primary_urls):
                url = p.get("url")
                if url:
                    await fetch_url(client, url, scheme_id, i)
                    await asyncio.sleep(1) # throttle

if __name__ == "__main__":
    asyncio.run(main())
