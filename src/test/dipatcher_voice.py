from src.router.dispatcher import dispatch_query
from src.voice.tts_piper import load_voice, text_to_speech_piper
from src.voice.sst_whisper import record_and_transcribe


def extract_response(result):
    """Extract readable text from common LangChain agent responses."""
    if isinstance(result, dict) and "messages" in result:
        messages = result["messages"]
        if messages:
            content = getattr(messages[-1], "content", None)
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                return " ".join(
                    item["text"]
                    for item in content
                    if isinstance(item, dict) and "text" in item
                )
    return str(result)


def main():
    print("=== Lumi Text + Voice Chat ===")
    
    try:
        voice = load_voice()
        print("Piper TTS loaded successfully.\n")
    except Exception as exc:
        print(f"Could not load Piper TTS: {exc}")
        return

    current_mode = None

    while True:
        # If mode is not set, ask user to choose
        if not current_mode:
            print("Choose an operating mode:")
            print("T = Text Mode | V = Voice Mode | Q = Quit\n")
            choice = input("Select mode [T/V/Q]: ").strip().lower()

            if choice in {"q", "quit", "exit"}:
                print("Lumi chat stopped.")
                break
            elif choice == "t":
                current_mode = "text"
                print("\n--- Switched to TEXT Mode (Type 'q' or 'quit' to change mode) ---\n")
            elif choice == "v":
                current_mode = "voice"
                print("\n--- Switched to VOICE Mode (Say or type 'q' or 'quit' to change mode) ---\n")
            else:
                print("Invalid choice. Please select T, V, or Q.\n")
                continue

        # --- TEXT MODE LOOP ---
        if current_mode == "text":
            query = input("You (Text) > ").strip()

            if query.lower() in {"q", "quit", "exit"}:
                print("\nExiting current mode. Returning to mode selection...\n")
                current_mode = None
                continue

            if not query:
                print("Please provide some input.\n")
                continue

        # --- VOICE MODE LOOP ---
        elif current_mode == "voice":
            print("Listening for voice input... (Speak now or type 'q' to change mode)")
            query = record_and_transcribe(duration=5)

            if not query:
                print("No speech recognized. Try again or say 'q' to switch modes.\n")
                continue

            print(f"You said > {query}")

            if query.lower() in {"q", "quit", "exit"}:
                print("\nExiting current mode. Returning to mode selection...\n")
                current_mode = None
                continue

        try:
            print("\nLumi is processing your request...\n")

            result = dispatch_query(query)
            response_text = extract_response(result)

            print(f"Lumi > {response_text}\n")

            # Speak response (press spacebar to pause/resume)
            text_to_speech_piper(response_text, voice)

        except Exception as exc:
            print(f"Execution error: {exc}")

        print()


if __name__ == "__main__":
    main()