
import requests
import feedparser
from difflib import SequenceMatcher

from src.config import (
    ARXIV_API_URL,
    ARXIV_USER_AGENT,
    ARXIV_TIMEOUT,
    ARXIV_SORT_BY,
    ARXIV_SORT_ORDER,
    ARXIV_FETCH_MULTIPLIER,
    ARXIV_FETCH_MIN,
    ARXIV_TOOL_DEFAULT_MAX_RESULTS,
    ARXIV_TOOL_MAX_RESULTS_LIMIT,
)

API_URL = ARXIV_API_URL

HEADERS = {
    "User-Agent": ARXIV_USER_AGENT
}


def search_papers(
    query,
    max_results=ARXIV_TOOL_DEFAULT_MAX_RESULTS,
    sort_by=ARXIV_SORT_BY,
):
    query = query.strip()

    if not query:
        return []

    max_results = max(1, min(int(max_results), ARXIV_TOOL_MAX_RESULTS_LIMIT))

    params = {
        "search_query": f'ti:"{query}"',
        "start": 0,
        "max_results": max(max_results * ARXIV_FETCH_MULTIPLIER, ARXIV_FETCH_MIN),
        "sortBy": sort_by,
        "sortOrder": ARXIV_SORT_ORDER,
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=ARXIV_TIMEOUT,
        )
        response.raise_for_status()

        feed = feedparser.parse(response.text)
        entries = list(feed.entries)

        # Fall back to all searchable fields if title
        # search returns no entries.
        if not entries:
            params["search_query"] = f"all:{query}"

            response = requests.get(
                API_URL,
                params=params,
                headers=HEADERS,
                timeout=ARXIV_TIMEOUT,
            )
            response.raise_for_status()

            feed = feedparser.parse(response.text)
            entries = list(feed.entries)

        papers = []

        for entry in entries:
            title = " ".join(
                getattr(entry, "title", "").split()
            )

            if not title:
                continue

            similarity = SequenceMatcher(
                None,
                query.lower(),
                title.lower(),
            ).ratio()

            authors = [
                author.name
                for author in getattr(entry, "authors", [])
                if getattr(author, "name", None)
            ]

            papers.append({
                "title": title,
                "authors": authors,
                "published": getattr(entry, "published", ""),
                "abstract": " ".join(
                    getattr(entry, "summary", "").split()
                ),
                "arxiv_id": entry.id.split("/abs/")[-1],
                "url": entry.link,
                "title_similarity": round(similarity, 3),
            })

        papers.sort(
            key=lambda paper: paper["title_similarity"],
            reverse=True,
        )

        return papers[:max_results]

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not retrieve papers from arXiv: {exc}"
        ) from exc
