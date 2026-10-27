from src.voice.sst_whisper import record_and_transcribe

def test_record_and_transcribe():
    print("\n=== STT Test ===")

    result = record_and_transcribe(duration=5)

    if result:
        print("\nTranscription successful!")
        print(f"Recognized text: {result}")
    else:
        print("\nTranscription failed or no speech was recognized.")


if __name__ == "__main__":
    test_record_and_transcribe()
