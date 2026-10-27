
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
MODEL_SIZE = "base"
DEVICE = "cuda"
COMPUTE_TYPE = "float16"

# Load the model once when the module is imported
print(f"Loading Faster-Whisper {MODEL_SIZE} on {DEVICE}...")

model = WhisperModel(
    MODEL_SIZE,
    device=DEVICE,
    compute_type=COMPUTE_TYPE,
)

print("Faster-Whisper Base ready!")


def record_and_transcribe(duration=5, sample_rate=SAMPLE_RATE):
    print(f"\nRecording for {duration} seconds... Speak now!")

    try:
        audio_data = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        audio_data = audio_data.squeeze()

        print("Recording finished. Transcribing locally...")

        segments, info = model.transcribe(
            audio_data,
            language="en",
            beam_size=1,
            vad_filter=True,
        )

        # Iterate over segments to run inference
        transcription = " ".join(
            segment.text.strip() for segment in segments
        ).strip()

        print("Transcription:", transcription or "(No speech detected)")
        return transcription or None

    except Exception as e:
        print(f"Error during local transcription: {e}")
        return None
    

