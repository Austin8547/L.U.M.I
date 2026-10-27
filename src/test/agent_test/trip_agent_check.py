import time

from src.agent.route_planner_agent import trip_planner_agent

QUERY = "Find driving routes from Trivandrum to Kochi."


def run_check(query: str = QUERY, show_steps: bool = False) -> None:
    start = time.time()

    try:
        response = trip_planner_agent.invoke({
            "messages": [{"role": "user", "content": query}]
        })
    except Exception as e:
        print(f"\n[FAILED after {time.time() - start:.1f}s] "
              f"{type(e).__name__}: {e}")
        return

    elapsed = time.time() - start
    messages = response["messages"]

    # Count tool calls the model made (should be 1 for this query)
    tool_calls = [
        tc
        for m in messages
        for tc in (getattr(m, "tool_calls", None) or [])
    ]

    # Optional: show every step (Human, AI tool call, Tool result, AI answer)
    if show_steps:
        print("=" * 60)
        for m in messages:
            m.pretty_print()

    print("=" * 60)
    print("FINAL ANSWER")
    print("=" * 60)
    print(messages[-1].content)

    print("\n" + "=" * 60)
    print("DEBUG")
    print("=" * 60)
    print(f"Total time      : {elapsed:.1f}s")
    print(f"Tool calls made : {len(tool_calls)}")
    for tc in tool_calls:
        print(f"  - {tc['name']}({tc['args']})")

    # Flag tool errors so a silent failure doesn't look like success
    for m in messages:
        if m.type == "tool" and '"error"' in str(m.content):
            print(f"\n[TOOL ERROR] {m.content}")


if __name__ == "__main__":
    run_check(show_steps=False)