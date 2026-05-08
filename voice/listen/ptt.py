"""
voice/listen/ptt.py - Lila's ears, Phase 2: Push-To-Talk.

Hold the hotkey (F9 by default), speak, release. The transcript gets
typed into whichever window currently has focus - so when Claude Code's
prompt is focused, your words land right there.

Run this in its OWN terminal (not Claude Code's), then alt-tab back to
Claude Code:

    voice\\listen\\.venv\\Scripts\\python.exe voice\\listen\\ptt.py

Hold F9, speak, release. Press Esc to quit.

Flags:
  --hotkey f9          push-to-talk key (try: f9, f10, space, scroll_lock)
  --model base.en      whisper model size
  --no-type            print transcript instead of typing it
  --type-delay 0.18    seconds to wait after release before typing
"""
import argparse
import threading
import time

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
from pynput import keyboard

SAMPLE_RATE = 16000
CHANNELS = 1
MIN_PRESS_SECONDS = 0.2  # ignore taps shorter than this


def parse_hotkey(name: str):
    """Return a pynput key object for a name like 'f9', 'space', 'a'."""
    if hasattr(keyboard.Key, name):
        return getattr(keyboard.Key, name)
    if len(name) == 1:
        return keyboard.KeyCode.from_char(name)
    raise ValueError(f"unknown hotkey: {name!r}")


def main():
    ap = argparse.ArgumentParser(description="Lila's ears - push-to-talk.")
    ap.add_argument("--hotkey", default="f9", help="push-to-talk key (default f9)")
    ap.add_argument("--model", default="base.en")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute-type", default="int8")
    ap.add_argument("--no-type", action="store_true",
                    help="print transcript instead of typing into focused window")
    ap.add_argument("--type-delay", type=float, default=0.18,
                    help="seconds to wait after release before typing (default 0.18)")
    ap.add_argument("--vad", action="store_true",
                    help="enable VAD filter (skips silence; may miss soft speech)")
    ap.add_argument("--debug", action="store_true",
                    help="print RMS level for each recording")
    args = ap.parse_args()

    target_key = parse_hotkey(args.hotkey)

    print(f"[ptt] loading whisper {args.model} on {args.device}/{args.compute_type}...")
    t0 = time.time()
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    print(f"[ptt] model loaded in {time.time() - t0:.1f}s.")
    print(f"[ptt] ready. Hold {args.hotkey.upper()} to talk. Press Esc to quit.")

    audio_chunks = []
    is_recording = threading.Event()
    press_started_at = [0.0]
    kb_controller = keyboard.Controller()
    transcribe_lock = threading.Lock()

    def audio_callback(indata, frames, time_info, status):
        if is_recording.is_set():
            audio_chunks.append(indata.copy())

    stream = sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        callback=audio_callback,
    )
    stream.start()

    def do_transcribe(audio: np.ndarray):
        if audio.size == 0:
            return
        duration = len(audio) / SAMPLE_RATE
        if duration < 0.3:
            print(f"[ptt] (too short: {duration:.2f}s, skipped)")
            return
        rms = float(np.sqrt(np.mean(audio ** 2)))
        if args.debug:
            print(f"[ptt] audio rms={rms:.4f} duration={duration:.2f}s")
        with transcribe_lock:
            t1 = time.time()
            segments, _ = model.transcribe(audio, language="en", vad_filter=args.vad)
            text = " ".join(s.text.strip() for s in segments).strip()
            elapsed = time.time() - t1
        if not text:
            print(f"[ptt] (no speech, {duration:.1f}s captured, {elapsed:.2f}s)")
            return
        print(f"[ptt] heard ({duration:.1f}s -> {elapsed:.2f}s): {text}")
        if args.no_type:
            return
        time.sleep(args.type_delay)
        kb_controller.type(text)

    def on_press(key):
        if key == target_key and not is_recording.is_set():
            audio_chunks.clear()
            is_recording.set()
            press_started_at[0] = time.time()
            print("[ptt] recording...", end="\r", flush=True)

    def on_release(key):
        if key == keyboard.Key.esc:
            print("[ptt] quitting.")
            return False
        if key == target_key and is_recording.is_set():
            is_recording.clear()
            held = time.time() - press_started_at[0]
            chunks = list(audio_chunks)
            audio_chunks.clear()
            if held < MIN_PRESS_SECONDS or not chunks:
                print(f"[ptt] (tap {held*1000:.0f}ms, skipped)")
                return True
            audio = np.concatenate(chunks).flatten()
            threading.Thread(target=do_transcribe, args=(audio,), daemon=True).start()
        return True

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    stream.stop()
    stream.close()


if __name__ == "__main__":
    main()
