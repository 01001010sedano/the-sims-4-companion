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

def date_from_title(title):
    match = re.search(r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4}", title or "")
    return match.group(0) if match else None

def fetch():
    request = Request(SOURCE, headers={"User-Agent": "PlumbobCompanion/0.1 (+GitHub Actions)"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")

def extract(html):
    # EA currently exposes the news feed in Next.js page data. Prefer this
    # structured payload over visual CSS selectors or generated page text.
    next_data = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S)
    if next_data:
        try:
            page = json.loads(next_data.group(1)).get("props", {}).get("pageProps", {})
            feed = page.get("initialNewsData", {}).get("items", [])
            if feed:
                latest = feed[0]
                title = clean(latest.get("title")) or None
                summary = clean(latest.get("summary")) or None
                url = latest.get("url") or latest.get("link") or SOURCE
                release_date = latest.get("date") or latest.get("publishedAt") or latest.get("datePublished") or date_from_title(title)
                return {
                    "source": url,
                    "checkedAt": datetime.now(timezone.utc).isoformat(),
                    "gameVersion": None,
                    "releaseDate": release_date,
                    "title": title,
                    "summary": summary,
                    "sections": [{"title": latest.get("type", "Official update"), "items": [title] if title else []}]
                }
        except (KeyError, TypeError, json.JSONDecodeError):
            pass

    # Fallback: prefer JSON-LD because it is more stable than visual CSS selectors.
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
