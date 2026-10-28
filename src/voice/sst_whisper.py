
import sounddevice as sd
from faster_whisper import WhisperModel

from src.config import (
    WHISPER_MODEL_SIZE,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_SAMPLE_RATE,
    WHISPER_RECORD_DURATION,
    WHISPER_BEAM_SIZE,
    WHISPER_VAD_FILTER,
    WHISPER_LANGUAGE,
)

SAMPLE_RATE = WHISPER_SAMPLE_RATE
MODEL_SIZE = WHISPER_MODEL_SIZE
DEVICE = WHISPER_DEVICE
COMPUTE_TYPE = WHISPER_COMPUTE_TYPE

# Load the model once when the module is imported
print(f"Loading Faster-Whisper {MODEL_SIZE} on {DEVICE}...")

model = WhisperModel(
    MODEL_SIZE,
    device=DEVICE,
    compute_type=COMPUTE_TYPE,
)

print("Faster-Whisper Base ready!")


def record_and_transcribe(duration=WHISPER_RECORD_DURATION, sample_rate=WHISPER_SAMPLE_RATE):
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
            language=WHISPER_LANGUAGE,
            beam_size=WHISPER_BEAM_SIZE,
            vad_filter=WHISPER_VAD_FILTER,
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
    

