
from src.voice.tts_piper import load_voice, text_to_speech_piper


def main():
    voice = load_voice()

    text = "Hello! I am Lumi, your personal AI assistant."
    text_to_speech_piper(text, voice)


if __name__ == "__main__":
    main()