from src.news.news_fetch import NewsFetcher
from langchain_core.tools import tool
from src.config import (
    NEWS_DEFAULT_LIMIT,
    NEWS_SUMMARY_MAX_CHARS,
    NEWS_TOOL_MIN_LIMIT,
    NEWS_TOOL_MAX_LIMIT,
)


@tool
def fetch_news(query: str, limit: int = NEWS_DEFAULT_LIMIT) -> str:
    """
    Fetch recent news headlines and short summaries.

    Use this tool when the user asks for news about a topic, person,
    location, business, technology, or a supported news category.

    Examples:
    - query="national"
    - query="Kerala"
    - query="Indian stock market"
    - query="Pinarayi Vijayan"

    Args:
        query: News category or topic to search for.
        limit: Number of articles to return, between 1 and 5.

    Returns:
        A formatted string containing article titles, publication dates,
        and short summaries. Does not call an LLM.
    """
    query = query.strip()

    if not query:
        return "Please provide a news topic or category."

    if not NEWS_TOOL_MIN_LIMIT <= limit <= NEWS_TOOL_MAX_LIMIT:
        return f"The article limit must be between {NEWS_TOOL_MIN_LIMIT} and {NEWS_TOOL_MAX_LIMIT}."

    try:
        articles = NewsFetcher.fetch_news(
            query=query,
            limit=limit,
        )

        if not articles:
            return f"No news articles found for '{query}'."

        results = [
            f"News results for: {query}",
            f"Articles found: {len(articles)}",
            "",
        ]

        for index, article in enumerate(articles, start=1):
            title = article.title.strip()
            published = article.published or "Unknown"
            summary = article.summary.strip()

            # Keep tool output compact to reduce LLM context usage.
            if len(summary) > NEWS_SUMMARY_MAX_CHARS:
                summary = summary[:NEWS_SUMMARY_MAX_CHARS].rsplit(" ", 1)[0] + "..."

            results.extend([
                f"{index}. {title}",
                f"Published: {published}",
                f"Summary: {summary or 'No summary available.'}",
                "",
            ])

        return "\n".join(results).strip()

    except Exception as exc:
        return (
            f"Unable to fetch news for '{query}'. "
            f"Check the internet connection and RSS feed availability. "
            f"Details: {type(exc).__name__}: {exc}"
        )
