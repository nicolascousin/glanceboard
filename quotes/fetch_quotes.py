#!/usr/bin/env python3
"""Fetch and classify free quote data for Glanceboard."""

import json
import re
import shutil
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUTS = [
    ROOT / "quotes" / "quotes.json",
    ROOT / "web" / "public" / "quotes.json",
]

THEME_KEYWORDS = {
    "humour": {"funny", "laugh", "humor", "joke", "ridiculous", "comedy"},
    "courage": {"brave", "courage", "fear", "bold", "dare"},
    "curiosite": {"curious", "question", "learn", "knowledge", "wonder"},
    "amitie": {"friend", "friendship", "together", "love", "kindness"},
    "perseverance": {"success", "failure", "persist", "work", "try"},
    "creativite": {"create", "creativity", "imagination", "art", "idea", "dream"},
    "famille": {"family", "parent", "child", "home", "mother", "father"},
    "ecole": {"school", "teacher", "education", "book", "study"},
    "animaux": {"dog", "cat", "bird", "animal", "horse", "fish"},
    "inspiration": {"dream", "life", "hope", "future", "change", "believe"},
}


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "Glanceboard quote catalog"})
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def classify(text):
    words = set(re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower()))
    scores = {theme: len(words.intersection(keywords)) for theme, keywords in THEME_KEYWORDS.items()}
    best_theme = max(scores, key=scores.get)
    return best_theme if scores[best_theme] else "inspiration"


def normalize(items):
    quotes = []
    seen = set()
    for item in items:
        text = item.get("q") or item.get("content") or item.get("quote") or ""
        text = re.sub(r"\s+", " ", text).strip().strip('"')
        if not text or len(text) > 240 or text.lower() in seen:
            continue
        seen.add(text.lower())
        quotes.append({"text": text, "theme": classify(text)})
    return quotes


def main():
    items = []
    sources = [
        "https://zenquotes.io/api/quotes",
        "https://api.quotable.io/quotes?limit=150",
    ]
    for source in sources:
        try:
            payload = fetch_json(source)
            items.extend(payload if isinstance(payload, list) else payload.get("results", []))
        except Exception as error:
            print(f"Warning: could not fetch {source}: {error}")

    quotes = normalize(items)
    if not quotes:
        raise SystemExit("No quotes were fetched; keeping the existing catalog.")

    payload = json.dumps(quotes, ensure_ascii=False, indent=2) + "\n"
    OUTPUTS[0].write_text(payload, encoding="utf-8")
    for output in OUTPUTS[1:]:
        shutil.copyfile(OUTPUTS[0], output)
    print(f"Saved {len(quotes)} quotes to {len(OUTPUTS)} files.")


if __name__ == "__main__":
    main()
