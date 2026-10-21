
import requests
import feedparser
from difflib import SequenceMatcher

API_URL = "https://export.arxiv.org/api/query"

HEADERS = {
    "User-Agent": "LumiResearchAgent/1.0 (arXiv paper search)"
}


def search_papers(query, max_results=3, sort_by="relevance"):
    query = query.strip()

    if not query:
        return []

    max_results = max(1, min(int(max_results), 10))

    params = {
        "search_query": f'ti:"{query}"',
        "start": 0,
        "max_results": max(max_results * 5, 25),
        "sortBy": sort_by,
        "sortOrder": "descending",
    }

    try:
        response = requests.get(
            API_URL,
            params=params,
            headers=HEADERS,
            timeout=30,
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
                timeout=30,
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
