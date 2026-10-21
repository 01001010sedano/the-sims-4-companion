#!/usr/bin/env python3
"""Fetch official Sims 4 news metadata into the static site's data file.

This intentionally stores only source-backed metadata and links. If EA changes
its markup, the workflow keeps the previous data instead of inventing values.
"""
import json
import re
import sys
from datetime import datetime, timezone
from html import unescape
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = "https://www.ea.com/games/the-sims/the-sims-4/news"
OUTPUT = Path(__file__).resolve().parents[1] / "data" / "updates.json"

def clean(value):
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", unescape(value)).strip()

def fetch():
    request = Request(SOURCE, headers={"User-Agent": "PlumbobCompanion/0.1 (+GitHub Actions)"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")

def extract(html):
    # Prefer JSON-LD because it is more stable than visual CSS selectors.
    blocks = re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', html, re.I | re.S)
    articles = []
    for block in blocks:
        try:
            parsed = json.loads(block.strip())
        except json.JSONDecodeError:
            continue
        values = parsed if isinstance(parsed, list) else [parsed]
        for item in values:
            if isinstance(item, dict) and item.get("@type") in ("NewsArticle", "Article", "BlogPosting"):
                articles.append(item)
    if not articles:
        raise RuntimeError("No official article metadata found; preserving previous data")
    articles.sort(key=lambda item: item.get("datePublished", ""), reverse=True)
    latest = articles[0]
    return {
        "source": latest.get("url") or SOURCE,
        "checkedAt": datetime.now(timezone.utc).isoformat(),
        "gameVersion": None,
        "releaseDate": latest.get("datePublished"),
        "title": clean(latest.get("headline")) or None,
        "summary": clean(latest.get("description")) or None,
        "sections": [{"title": "Official article", "items": [clean(latest.get("headline"))]}]
    }

def main():
    try:
        data = extract(fetch())
    except Exception as error:
        print(f"Update fetch skipped: {error}", file=sys.stderr)
        return 1
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT}")

if __name__ == "__main__":
    sys.exit(main())
