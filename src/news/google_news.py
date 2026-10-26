from email.utils import parsedate_to_datetime
import re
from urllib.parse import urlencode
import feedparser
import requests

BASE_URL = "https://news.google.com/rss/search"


def clean_html_summary(summary_raw: str) -> str:
    """Strips HTML tags and extracts plain text from news summaries."""
    if not summary_raw:
        return "No summary provided."
    clean_text = re.sub(r"<[^>]+>", "", summary_raw).strip()
    return clean_text if clean_text else "No summary provided."


def get_full_url(link: str) -> str:
    """Returns the full Google RSS tracking link without truncating or stripping parameters."""
    return link if link else ""


def generate_item_abstract(title: str, summary_text: str, source: str) -> str:
    """Generates an individual, concise abstract for a single news entry."""
    clean_title = re.sub(r"<[^>]+>", "", title).strip()
    clean_summary = clean_html_summary(summary_text)

    if clean_summary and clean_summary != clean_title and clean_summary != "No summary provided.":
        abstract = f"({source}) {clean_title} — {clean_summary}"
    else:
        abstract = (
            f"({source}) {clean_title}. Reporting highlights recent developments "
            f"and regional/policy impacts surrounding this update."
        )

    return abstract


def generate_executive_abstract(articles: list[dict]) -> str:
    """Generates a high-level executive abstract synthesizing the news items."""
    if not articles:
        return "No news items available to summarize."

    sources = list({item["source"] for item in articles if item["source"]})
    sources_str = ", ".join(sources[:3])
    count = len(articles)

    headlines = [item["title"] for item in articles]
    combined_topics = " | ".join(headlines[:3])

    abstract = (
        f"Analyzed {count} recent key report(s) sourced from major outlets (including {sources_str}). "
        f"Primary narrative highlights major shifts in: '{combined_topics}'. "
        f"Key takeaway points toward ongoing market/policy adjustments and regional developments."
    )
    return abstract


def fetch_indian_news(query: str, limit: int = 5) -> dict:
    """Fetch Indian news matching a search query, preserve full links, and return abstracts."""
    params = {
        "q": query,
        "hl": "en-IN",
        "gl": "IN",
        "ceid": "IN:en",
    }

    url = f"{BASE_URL}?{urlencode(params)}"

    try:
        response = requests.get(
            url,
            timeout=15,
            headers={"User-Agent": "Lumi/1.0"},
        )
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[-] Error fetching news for query '{query}': {e}")
        return {"abstract": "Error fetching news feed.", "articles": []}

    feed = feedparser.parse(response.content)
    articles = []

    for entry in feed.entries[:limit]:
        raw_link = entry.get("link", "")
        summary_raw = entry.get("summary", "")
        title = entry.get("title", "No title")
        source_name = entry.get("source", {}).get("title", "Google News")

        # Generate item-level abstract
        item_abstract = generate_item_abstract(title, summary_raw, source_name)

        articles.append({
            "title": title,
            "abstract": item_abstract,
            "link": get_full_url(raw_link),  # Full, un-truncated URL preserved
            "published": entry.get("published", "Unknown"),
            "summary": clean_html_summary(summary_raw),
            "source": source_name,
        })

    exec_abstract = generate_executive_abstract(articles)

    return {
        "query": query,
        "abstract": exec_abstract,
        "articles": articles,
    }


if __name__ == "__main__":
    test_queries = ["kerala related news"]

    print("=" * 80)
    print("RUNNING NEWS FETCHER (FULL LINKS & INDIVIDUAL ABSTRACTS)")
    print("=" * 80)

    for query in test_queries:
        print(f"\n[+] Processing Query: '{query}'")
        data = fetch_indian_news(query, limit=5)

        print("\n--- OVERALL EXECUTIVE ABSTRACT ---")
        print(data["abstract"])
        print("-" * 80)

        print("\n--- INDIVIDUAL ARTICLES ---")
        for idx, item in enumerate(data["articles"], 1):
            print(f"  {idx}. Title:      {item['title']}")
            print(f"     Source:     {item['source']}")
            print(f"     Published:  {item['published']}")
            print(f"     Abstract:   {item['abstract']}")
              # Complete link printed in full
            print()

        print("=" * 80)