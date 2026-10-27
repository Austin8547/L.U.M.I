
from src.memory.memory import ConversationMemory


def main():
    memory = ConversationMemory()

    # Create a new conversation.
    session_id = memory.create_session()
    print("Session ID:", session_id)

    # Save a conversation.
    memory.save_message(
        session_id, "user", "My project is Lumi."
    )
    memory.save_message(
        session_id, "assistant", "Great! Let's work on Lumi."
    )
    memory.save_message(
        session_id, "user", "I want to add a coding agent."
    )

    # Retrieve the conversation.
    history = memory.get_history(session_id)

    print("\nRetrieved conversation:")
    for message in history:
        print(f"{message['role']}: {message['content']}")

    # Create another memory instance to verify persistence.
    memory_again = ConversationMemory()
    print("\nPersistence check:")
    print(memory_again.get_history(session_id))


if __name__ == "__main__":
    main()
