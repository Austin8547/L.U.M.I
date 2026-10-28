
from langchain_tavily import TavilySearch

from src.config import (
    TAVILY_MAX_RESULTS,
    TAVILY_TOPIC,
    TAVILY_SEARCH_DEPTH,
    TAVILY_INCLUDE_ANSWER,
    TAVILY_INCLUDE_RAW_CONTENT,
)

tavily = TavilySearch(
    max_results=TAVILY_MAX_RESULTS,
    topic=TAVILY_TOPIC,
    search_depth=TAVILY_SEARCH_DEPTH,
    include_answer=TAVILY_INCLUDE_ANSWER,
    include_raw_content=TAVILY_INCLUDE_RAW_CONTENT,
)


def tavily_web_search(query: str) -> str:
    """Search the web using Tavily and return formatted results."""

    response = tavily.invoke({"query": query})
    results = response.get("results", [])

    if not results:
        return "No relevant web search results found."

    formatted_results = []

    for i, result in enumerate(results, start=1):
        formatted_results.append(
            f"Result {i}\n"
            f"Title: {result.get('title', 'N/A')}\n"
            f"URL: {result.get('url', 'N/A')}\n"
            f"Content: {result.get('content', 'N/A')}"
        )

    return "\n\n".join(formatted_results)
