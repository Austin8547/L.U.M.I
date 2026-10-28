
from typing import Any
from src.config import (
    CONTEXT_MAX_MESSAGES,
    CONTEXT_MAX_CHARS,
    CONTEXT_MIN_REMAINING_CHARS,
)


def prepare_context(
    history: list[dict[str, Any]] | None,
    max_messages: int = CONTEXT_MAX_MESSAGES,
    max_chars: int = CONTEXT_MAX_CHARS,
) -> list[dict[str, str]]:
    """
    Prepare a compact conversation history for an LLM.

    Keeps recent messages under a character budget.
    The original stored history is never modified.
    """

    if not history:
        return []

    selected = []
    total_chars = 0

    # Process newest messages first.
    for message in reversed(history):
        role = str(message.get("role", "user"))
        content = str(message.get("content", ""))

        if not content.strip():
            continue

        cost = len(role) + len(content)

        if len(selected) >= max_messages:
            break

        if total_chars + cost > max_chars:
            remaining = max_chars - total_chars - len(role)

            # Skip an oversized message rather than cutting it mid-sentence.
            if remaining < CONTEXT_MIN_REMAINING_CHARS:
                break

            content = content[-remaining:]
            cost = len(role) + len(content)

        selected.append({
            "role": role,
            "content": content,
        })
        total_chars += cost

        if total_chars >= max_chars:
            break

    # Restore chronological order.
    return list(reversed(selected))
