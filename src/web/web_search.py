
from dotenv import load_dotenv
from langchain_tavily import TavilySearch

load_dotenv()

tavily = TavilySearch(
    max_results=3,
    topic="general",
    search_depth="basic",
    include_answer=False,
    include_raw_content=False,
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
