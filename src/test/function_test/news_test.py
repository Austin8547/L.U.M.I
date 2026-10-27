from src.news.news_fetch import NewsFetcher
if __name__ == "__main__":
    query_term = input(
        "Enter a news topic or category: "
    ).strip()

    if not query_term:
        print("Please enter a valid search query.")
        raise SystemExit(1)

    try:
        limit_input = input(
            "Number of articles (default 3): "
        ).strip()

        limit = int(limit_input) if limit_input else 3

        if limit <= 0:
            raise ValueError(
                "Number of articles must be greater than zero."
            )

        print(f"\nFetching news for '{query_term}'...\n")

        # Fetch the combined briefing and individual articles
        overall_summary, news_items = (
            NewsFetcher.get_news_with_abstract(
                query=query_term,
                limit=limit
            )
        )

        print("=" * 60)
        print("BRIEF NEWS SUMMARY")
        print("=" * 60)
        print(overall_summary)

        if news_items:
            print("\n" + "=" * 60)
            print("DETAILED ARTICLES")
            print("=" * 60)

            for idx, article in enumerate(news_items, 1):
                print(f"\n[{idx}] {article.title}")
                print(f"Published: {article.published}")
                print(f"Summary: {article.summary}")

        else:
            print("\nNo articles were available for this query.")

    except ValueError as error:
        print(f"Invalid input: {error}")

    except Exception as error:
        print(f"Error fetching news: {error}")


