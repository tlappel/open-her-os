"""
voice/listen/listen.py - Lila's ears (Phase 1).

Records a few seconds of audio from your default mic, transcribes
it locally with faster-whisper, and prints the transcript.

Usage:
    python voice/listen/listen.py            # default 5s recording
    python voice/listen/listen.py -d 8       # record for 8 seconds
    python voice/listen/listen.py --model small.en

Phase 2 (push-to-talk + auto-type into Claude Code) will come next.
"""
import argparse
import sys
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel

SAMPLE_RATE = 16000
CHANNELS = 1


def record(duration_s: float) -> np.ndarray:
    print(f"[listen] recording {duration_s:.1f}s - start talking...", flush=True)
    audio = sd.rec(
        int(duration_s * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
    )
    for i in range(int(duration_s), 0, -1):
        print(f"  {i}... ", end="\r", flush=True)
        time.sleep(1)
    sd.wait()
    print("[listen] done recording.        ")
    return audio.flatten()


def transcribe(audio: np.ndarray, model_size: str, device: str, compute_type: str) -> str:
    print(f"[listen] loading whisper model: {model_size} on {device} ({compute_type})...")
    t0 = time.time()
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    print(f"[listen] model loaded in {time.time() - t0:.1f}s. transcribing...")
    t0 = time.time()
    segments, _info = model.transcribe(audio, language="en", vad_filter=True)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    print(f"[listen] transcribed in {time.time() - t0:.1f}s.")
    return text


def main():
    parser = argparse.ArgumentParser(description="Lila's ears - local Whisper STT.")
    parser.add_argument("-d", "--duration", type=float, default=5.0,
                        help="seconds to record (default 5)")
    parser.add_argument("--model", default="base.en",
                        help="whisper model: tiny.en, base.en, small.en, medium.en, large-v3 (default base.en)")
    parser.add_argument("--device", default="cpu", help="cpu or cuda (default cpu)")
    parser.add_argument("--compute-type", default="int8",
                        help="int8, int8_float16, float16, float32 (default int8)")
    args = parser.parse_args()

    try:
        audio = record(args.duration)
    except Exception as e:
        print(f"[listen] mic error: {e}", file=sys.stderr)
        print("[listen] try: python -c \"import sounddevice; print(sounddevice.query_devices())\" "
              "to list devices", file=sys.stderr)
        sys.exit(1)

    text = transcribe(audio, args.model, args.device, args.compute_type)
    if text:
        print(f"\nyou said: {text}")
    else:
        print("\n(no speech detected)")


if __name__ == "__main__":
    main()
