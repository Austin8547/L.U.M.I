import time
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

# Recording settings
SAMPLE_RATE = 16000
DURATION = 10# seconds

print("Loading Whisper Tiny on RTX 3050...")

model = WhisperModel(
    "tiny",
    device="cuda",
    compute_type="float16",
)

print("Whisper Tiny loaded successfully!")


def record_audio():
    print(f"\nRecording for {DURATION} seconds... Speak now!")

    audio = sd.rec(
        int(DURATION * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="float32",
    )

    sd.wait()

    # Convert stereo-shaped array to mono 1D audio
    audio = np.squeeze(audio)

    print("Recording complete!")
    return audio


def transcribe_audio(audio):
    print("Transcribing on GPU...")

    start = time.perf_counter()

    segments, info = model.transcribe(
        audio,
        language="en",
        beam_size=1,
    )

    # Consume the generator to perform transcription
    text = " ".join(segment.text.strip() for segment in segments)

    elapsed = time.perf_counter() - start

    print("\nDetected language:", info.language)
    print("Transcription:", text or "(No speech detected)")
    print(f"Transcription time: {elapsed:.2f} seconds")


if __name__ == "__main__":
    try:
        while True:
            input("\nPress Enter to record, or Ctrl+C to exit...")
            audio = record_audio()
            transcribe_audio(audio)

    except KeyboardInterrupt:
        print("\nExiting Whisper STT test.")