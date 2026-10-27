
from dataclasses import dataclass
from typing import List, Tuple
import urllib.parse
import re
import feedparser

# Optional HTML cleaner
try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False


@dataclass
class Article:
    title: str
    published: str
    summary: str


class NewsFetcher:
    """RSS news fetcher for L.U.M.I. assistant pipelines."""

    # Direct section mapping for The Hindu RSS feeds
    HINDU_FEEDS = {
        "home": "https://www.thehindu.com/feeder/default.rss",
        "national": "https://www.thehindu.com/news/national/feeder/default.rss",
        "international": "https://www.thehindu.com/news/international/feeder/default.rss",
        "editorial": "https://www.thehindu.com/opinion/editorial/feeder/default.rss",
        "opinion": "https://www.thehindu.com/opinion/feeder/default.rss",
        "business": "https://www.thehindu.com/business/feeder/default.rss",
        "economy": "https://www.thehindu.com/business/Economy/feeder/default.rss",
        "technology": "https://www.thehindu.com/sci-tech/technology/feeder/default.rss",
        "science": "https://www.thehindu.com/sci-tech/science/feeder/default.rss",
        "kerala": "https://www.thehindu.com/news/national/kerala/feeder/default.rss",
        "tamil nadu": "https://www.thehindu.com/news/national/tamil-nadu/feeder/default.rss",
        "karnataka": "https://www.thehindu.com/news/national/karnataka/feeder/default.rss",
    }

    @classmethod
    def _clean_text(cls, raw_text: str) -> str:
        """Remove HTML tags and normalize whitespace."""
        if not raw_text:
            return ""

        if HAS_BS4:
            text = BeautifulSoup(
                raw_text, "html.parser"
            ).get_text(separator=" ")
        else:
            text = re.sub(r"<[^>]+>", " ", raw_text)

        return " ".join(text.split())

    @classmethod
    def get_feed_url(cls, query: str) -> str:
        """Resolve a known category or search Google News for a custom query."""
        clean_query = query.strip().lower()

        if not clean_query:
            raise ValueError("Search query cannot be empty.")

        # Exact category matching
        if clean_query in cls.HINDU_FEEDS:
            return cls.HINDU_FEEDS[clean_query]

        # All other topics use Google News RSS
        encoded_query = urllib.parse.quote_plus(query.strip())

        return (
            "https://news.google.com/rss/search"
            f"?q={encoded_query}&hl=en-IN&gl=IN&ceid=IN:en"
        )

    @classmethod
    def fetch_news(
        cls,
        query: str = "national",
        limit: int = 5
    ) -> List[Article]:
        """Fetch news articles for a category or custom search query."""
        if limit <= 0:
            raise ValueError("Article limit must be greater than zero.")

        url = cls.get_feed_url(query)
        parsed_feed = feedparser.parse(url)

        if parsed_feed.bozo and not parsed_feed.entries:
            raise RuntimeError(
                f"Unable to read the news feed for '{query}'. "
                "Check your internet connection or RSS feed availability."
            )

        articles = []

        for entry in parsed_feed.entries[:limit]:
            title = cls._clean_text(
                entry.get("title", "No Title")
            )

            raw_summary = (
                entry.get("summary")
                or entry.get("description")
                or ""
            )

            summary = cls._clean_text(raw_summary)

            articles.append(
                Article(
                    title=title or "No Title",
                    published=entry.get("published", "Unknown"),
                    summary=summary or "No summary available.",
                )
            )

        return articles

    @classmethod
    def get_news_with_abstract(
        cls,
        query: str = "national",
        limit: int = 5
    ) -> Tuple[str, List[Article]]:
        """
        Return a brief combined news summary and individual articles.

        The combined summary is created from RSS headlines and descriptions.
        It is not an AI-generated summary.
        """
        articles = cls.fetch_news(query=query, limit=limit)

        if not articles:
            return f"No news items found for '{query}'.", []

        summary_lines = [
            f"Brief news update on {query}: "
            f"{len(articles)} articles found."
        ]

        for idx, article in enumerate(articles, 1):
            summary_lines.append(
                f"{idx}. {article.title}. {article.summary}"
            )

        brief_summary = " ".join(summary_lines)

        return brief_summary, articles
