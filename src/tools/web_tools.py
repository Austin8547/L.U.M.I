from src.web.web_search import tavily_web_search
from langchain_core.tools import tool


@tool
def web_search(query: str) -> str:
    """Search the web for relevant information, articles,
    documentation, and websites using Tavily.
    Returns page titles, URLs, and content snippets.
    """
    
    return tavily_web_search(query)


