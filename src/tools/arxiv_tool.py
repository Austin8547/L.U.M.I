from langchain_core.tools import tool

from src.arxiv.arxiv_search import search_papers
from src.config import ARXIV_TOOL_DEFAULT_MAX_RESULTS

import json


@tool
def arxiv_paper_search(
    query: str,
    max_results: int = ARXIV_TOOL_DEFAULT_MAX_RESULTS,
) -> str:
    """
    Search arXiv for research papers.

    Use this tool to find papers by title or research topic.
    Returns paper titles, authors, publication dates,
    abstracts, arXiv IDs, URLs, and title similarity scores.

    Args:
        query: Paper title or research topic.
        max_results: Number of papers to return, from 1 to 10.
    """
    papers = search_papers(
        query=query,
        max_results=max_results,
    )

    return json.dumps(
        papers,
        ensure_ascii=False,
        indent=2,
    )
