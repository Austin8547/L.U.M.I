from src.arxiv.arxiv_search import search_papers




def test_arxiv_search():
    query = "YOLO"

    results = search_papers(
        query=query,
        max_results=3,
    )

    if not results:
        print("No papers found.")
        return

    for i, paper in enumerate(results, start=1):
        print(f"\n{'=' * 60}")
        print(f"Paper {i}")
        print(f"{'=' * 60}")
        print("Title:", paper["title"])
        print("Authors:", ", ".join(paper["authors"]))
        print("Published:", paper["published"])
        print("Abstract:", paper["abstract"][:500])
        print("arXiv ID:", paper["arxiv_id"])
        print("Title similarity:", paper["title_similarity"])
        print("Link:", paper["url"])


if __name__ == "__main__":
    test_arxiv_search()
