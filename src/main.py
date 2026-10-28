

from src.router.dispatcher import dispatch_query
from src.memory.memory import ConversationMemory
from src.voice.tts_piper import load_voice, text_to_speech_piper
from src.voice.sst_whisper import record_and_transcribe
from src.config import WHISPER_RECORD_DURATION


def main():
    print("==== Hello I Am L.U.M.I Your Friendly AI Assistant =====")

    # Load Piper TTS.
    try:
        voice = load_voice()
        print("Piper TTS loaded successfully.\n")
    except Exception as exc:
        print(f"Could not load Piper TTS: {exc}")
        return

    # Create one conversation session for this launch.
    session_id = ConversationMemory.create_session()
    print(f"Lumi session: {session_id}\n")

    current_mode = None

    while True:

        # Mode selection.
        if not current_mode:
            print("Choose an operating mode:")
            print("T = Text Mode | V = Voice Mode | Q = Quit\n")

            choice = input("Select mode [T/V/Q]: ").strip().lower()

            if choice in {"q", "quit", "exit"}:
                print("Lumi chat stopped.")
                break

            elif choice == "t":
                current_mode = "text"
                print(
                    "\n--- Switched to TEXT Mode "
                    "(Type 'q' or 'quit' to change mode) ---\n"
                )

            elif choice == "v":
                current_mode = "voice"
                print(
                    "\n--- Switched to VOICE Mode "
                    "(Say or type 'q' to change mode) ---\n"
                )

            else:
                print("Invalid choice. Please select T, V, or Q.\n")
                continue

        # Text input.
        if current_mode == "text":
            query = input("You (Text) > ").strip()

            if query.lower() in {"q", "quit", "exit"}:
                print(
                    "\nExiting current mode. "
                    "Returning to mode selection...\n"
                )
                current_mode = None
                continue

            if not query:
                print("Please provide some input.\n")
                continue

        # Voice input.
        elif current_mode == "voice":
            print(
                "Listening for voice input... "
                "(Speak now or type 'q' to change modes)"
            )

            query = record_and_transcribe(duration=WHISPER_RECORD_DURATION)

            if not query or not query.strip():
                print(
                    "No speech recognized. "
                    "Try again or say 'q' to switch modes.\n"
                )
                continue

            query = query.strip()
            print(f"You said > {query}")

            if query.lower() in {"q", "quit", "exit"}:
                print(
                    "\nExiting current mode. "
                    "Returning to mode selection...\n"
                )
                current_mode = None
                continue

        # Dispatch the query using the current conversation session.
        try:
            print("\nLumi is processing your request...\n")

            response = dispatch_query(
                query,
                session_id=session_id,
            )

            # The dispatcher already extracts the assistant response.
            print(f"Lumi > {response}\n")

            # Speak the response using Piper TTS.
            if isinstance(response, str) and response.strip():
                text_to_speech_piper(response, voice)

        except Exception as exc:
            print(f"Execution error: {exc}")

        print()


if __name__ == "__main__":
    main()
