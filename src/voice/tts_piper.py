import os
import re
import numpy as np
import sounddevice as sd
import wave
import io
import threading
from piper import PiperVoice
import emoji

from src.voice.keyboard_listner import TerminalKeyListener

MODEL_NAME = "/home/austin/agentic/lumi/src/voice/files/en_US-lessac-medium.onnx"


def load_voice(model_path=MODEL_NAME):
    if not os.path.isfile(model_path):
        raise FileNotFoundError(f"Piper voice model not found: {model_path}")
    return PiperVoice.load(model_path)


def clean_text_for_tts(text: str) -> str:
    """Remove Markdown formatting and emojis before sending text to Piper."""
    text = emoji.replace_emoji(text, replace="")
    text = re.sub(r"\*{1,3}", "", text)
    text = re.sub(r"(?m)^\s*#+\s*", "", text)
    text = text.replace("`", "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def text_to_speech_piper(text, voice):
    if not text or not text.strip():
        print("No text provided for speech.")
        return

    text = clean_text_for_tts(text)
    if not text:
        print("No speakable text after cleaning.")
        return

    try:
        # Synthesize wav into memory
        wav_buffer = io.BytesIO()
        with wave.open(wav_buffer, "wb") as wav_file:
            voice.synthesize_wav(text, wav_file)

        wav_buffer.seek(0)

        with wave.open(wav_buffer, "rb") as wf:
            sample_rate = wf.getframerate()
            channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            frames = wf.readframes(wf.getnframes())

        if sampwidth == 2:
            audio_data = np.frombuffer(frames, dtype=np.int16)
        else:
            audio_data = np.frombuffer(frames, dtype=np.float32)

        if channels > 1:
            audio_data = audio_data.reshape((-1, channels))

        print("[Controls: SPACE = Pause/Resume | ENTER = Skip to next prompt]")

        is_paused = False
        stop_playback = False
        lock = threading.Lock()
        stop_listener = threading.Event()

        # Keyboard control thread
        def listen_for_keys():
            nonlocal is_paused, stop_playback
            with TerminalKeyListener() as listener:
                while not stop_listener.is_set():
                    key = listener.get_key()
                    if key is not None:
                        # Spacebar pressed
                        if key == " ":
                            with lock:
                                is_paused = not is_paused
                                if is_paused:
                                    print("\n[TTS Paused. Press SPACE to Resume]")
                                else:
                                    print("\n[TTS Resumed]")

                        # Enter key pressed (\n or \r)
                        elif key in ("\n", "\r"):
                            with lock:
                                stop_playback = True
                                print("\n[TTS Skipped. Moving to next input...]")
                            break
                    sd.sleep(10)

        listener_thread = threading.Thread(target=listen_for_keys, daemon=True)
        listener_thread.start()

        # Stream audio
        chunk_size = 1024
        stream = sd.OutputStream(samplerate=sample_rate, channels=channels, dtype="int16")
        stream.start()

        idx = 0
        total_len = len(audio_data)

        try:
            while idx < total_len:
                with lock:
                    if stop_playback:
                        break
                    paused = is_paused

                if paused:
                    sd.sleep(50)
                    continue

                end_idx = min(idx + chunk_size, total_len)
                chunk = audio_data[idx:end_idx]
                stream.write(chunk)
                idx = end_idx
        finally:
            stop_listener.set()
            stream.stop()
            stream.close()
            if not stop_playback:
                print("[TTS Finished]")

    except Exception as e:
        print(f"Audio playback failed: {e}")