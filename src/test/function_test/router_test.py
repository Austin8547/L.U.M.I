from src.router.llm_router import route_query



def main():
    print("=== Lumi Router Test ===")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        query = input("Lumi > ").strip()

        if query.lower() in {"exit", "quit"}:
            print("Lumi router stopped.")
            break

        if not query:
            print("Please enter a query.")
            continue

        try:
            agent_name = route_query(query)

            print(f"Selected agent: {agent_name}\n")

        except Exception as exc:
            print(f"Router error: {exc}\n")


if __name__ == "__main__":
    main()
