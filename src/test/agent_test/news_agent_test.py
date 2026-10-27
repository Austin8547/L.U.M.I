from src.agent.news_agent import news_agent

if __name__ == "__main__":
    print("=== Lumi News Agent Test ===")

    while True:
        query = input("\nEnter a news query (or 'q' to quit): ").strip()

        if query.lower() in {"q", "quit", "exit"}:
            print("Exiting Lumi News Agent.")
            break

        if not query:
            print("Please enter a valid news query.")
            continue

        try:
            result = news_agent.invoke({
                "messages": [
                    {"role": "user", "content": query}
                ]
            })

            messages = result.get("messages", [])
            if messages:
                print("\nLumi News:")
                print("-" * 50)
                print(messages[-1].content)
            else:
                print("No response received from the news agent.")

        except Exception as exc:
            print(f"Error running news agent: {exc}")
