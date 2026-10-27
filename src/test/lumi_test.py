
from src.router.dispatcher import dispatch_query


def main():
    print("=== Lumi Dispatcher Test ===")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        query = input("Lumi > ").strip()

        if query.lower() in {"exit", "quit"}:
            print("Dispatcher test stopped.")
            break

        if not query:
            print("Please enter a query.\n")
            continue

        try:
            print("\nRouting and executing...\n")

            result = dispatch_query(query)

            print("=== Agent Result ===")

            # Handle common LangChain agent responses.
            if isinstance(result, dict) and "messages" in result:
                print(result["messages"][-1].content)
            else:
                print(result)

            print()

        except Exception as exc:
            print(f"Execution error: {exc}\n")


if __name__ == "__main__":
    main()


