
from src.router.llm_router import route_query, chat_query
from src.memory.mem_middleware import prepare_context

from src.agent.arxiv_agent import arxiv_agent
from src.agent.utility_agent import system_resource_agent
from src.agent.route_planner_agent import trip_planner_agent
from src.agent.web_agent import web_agent
from src.agent.news_agent import news_agent
from src.memory.memory import ConversationMemory


AGENTS = {
    "arxiv": arxiv_agent,
    "resources": system_resource_agent,
    "trip": trip_planner_agent,
    "websearch": web_agent,
    "news":news_agent,
}

memory = ConversationMemory()


def extract_response(result):
    """Extract readable assistant text from an agent result."""

    if isinstance(result, str):
        return result

    if isinstance(result, dict):
        messages = result.get("messages", [])

        for message in reversed(messages):
            role = getattr(message, "type", None)
            content = getattr(message, "content", None)

            if isinstance(message, dict):
                role = message.get("role", role)
                content = message.get("content", content)

            if role not in {"assistant", "ai"}:
                continue

            if isinstance(content, str) and content.strip():
                return content

            if isinstance(content, list):
                parts = [
                    item["text"]
                    for item in content
                    if isinstance(item, dict)
                    and isinstance(item.get("text"), str)
                ]

                if parts:
                    return " ".join(parts)

    return str(result)


def dispatch_query(query: str, session_id: str):
    """Route a query to direct chat or a specialized agent."""

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    query = query.strip()

    # 1. Retrieve previous conversation history.
    full_history = memory.get_history(session_id, limit=20)
    history = prepare_context(
    full_history,
    max_messages=6,
    max_chars=3000,
    )

    # 2. Save the current user message.
    memory.save_message(session_id, "user", query)

    # 3. Choose a route using the previous conversation.
    route = route_query(query, chat_history=history)

    # 4. Handle ordinary conversation directly through the LLM.
    if route == "chat":
        try:
            response_text = chat_query(
                query,
                chat_history=history,
            )

            memory.save_message(
                session_id,
                "assistant",
                response_text,
            )

            return response_text

        except Exception as exc:
            print(f"[Lumi Dispatcher] Chat execution failed: {exc}")
            raise

    # 5. Find the appropriate specialized agent.
    agent = AGENTS.get(route)

    if agent is None:
        # Safe fallback if an unexpected route reaches the dispatcher.
        print(
            f"[Lumi Dispatcher] Unknown route {route!r}; "
            "falling back to direct chat."
        )

        response_text = chat_query(
            query,
            chat_history=history,
        )

        memory.save_message(
            session_id,
            "assistant",
            response_text,
        )

        return response_text

    # 6. Execute the selected agent with conversation history.
    messages = history + [
        {"role": "user", "content": query}
    ]

    try:
        result = agent.invoke({"messages": messages})
        response_text = extract_response(result)

        memory.save_message(
            session_id,
            "assistant",
            response_text,
        )

        return response_text

    except Exception as exc:
        print(f"[Lumi Dispatcher] Agent execution failed: {exc}")
        raise
