import time, queue, collections
import numpy as np
import sounddevice as sd
import torch
from silero_vad import load_silero_vad, VADIterator
from transformers import AutoProcessor, MoonshineForConditionalGeneration

SR = 16000
CHUNK = 512                 # Silero needs 512 samples at 16 kHz (32 ms)
MAX_SECONDS = 20            # force a transcription if someone talks this long
PREROLL_CHUNKS = 10         # ~0.3 s kept before speech starts so words aren't clipped

device = "cuda" if torch.cuda.is_available() else "cpu"
dtype = torch.float16 if device == "cuda" else torch.float32
name = "UsefulSensors/moonshine-base"   # try moonshine-tiny for lower latency

print(f"Loading Moonshine on {device}...")
processor = AutoProcessor.from_pretrained(name)
model = MoonshineForConditionalGeneration.from_pretrained(name, torch_dtype=dtype).to(device).eval()

vad_model = load_silero_vad()
vad = VADIterator(vad_model, sampling_rate=SR, threshold=0.5,
                  min_silence_duration_ms=600, speech_pad_ms=100)

def transcribe(audio_np):
    inputs = processor(audio_np, sampling_rate=SR, return_tensors="pt").to(device, dtype)
    max_len = int(len(audio_np) / SR * 6.5) + 10
    with torch.inference_mode():
        ids = model.generate(**inputs, max_new_tokens=max_len)
    return processor.batch_decode(ids, skip_special_tokens=True)[0].strip()

# warm-up so the first real utterance isn't slow
transcribe(np.zeros(SR, dtype=np.float32))

q = queue.Queue()
def callback(indata, frames, t, status):
    if status:
        print(status)
    q.put(indata[:, 0].copy())

print("Listening... speak, then pause. Ctrl+C to stop.\n")
preroll = collections.deque(maxlen=PREROLL_CHUNKS)
speech = []
speaking = False

try:
    with sd.InputStream(samplerate=SR, channels=1, dtype="float32",
                        blocksize=CHUNK, callback=callback):
        while True:
            chunk = q.get()
            event = vad(torch.from_numpy(chunk))

            if event and "start" in event and not speaking:
                speaking = True
                speech = list(preroll)

            if speaking:
                speech.append(chunk)

            too_long = speaking and len(speech) * CHUNK / SR >= MAX_SECONDS
            if (event and "end" in event and speaking) or too_long:
                audio = np.concatenate(speech)
                t0 = time.time()
                text = transcribe(audio)
                dt = time.time() - t0
                if text:
                    print(f"> {text}   ({dt:.2f}s for {len(audio)/SR:.1f}s audio)")
                speaking, speech = False, []
                vad.reset_states()
            elif not speaking:
                preroll.append(chunk)

except KeyboardInterrupt:
    print("\nStopped.")