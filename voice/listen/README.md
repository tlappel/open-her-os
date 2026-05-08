# voice/listen — Lila's Ears

Local speech-to-text so you can **talk** to your AI companion instead of typing. Runs 100% on your machine via [faster-whisper](https://github.com/SYSTRAN/faster-whisper) — no audio ever leaves your computer.

## Phase 1 (current): Fixed-duration recording

Press Enter, talk for N seconds, see your transcript. Proves the pipeline.

```powershell
# from the repo root
voice\listen\.venv\Scripts\python.exe voice\listen\listen.py            # 5s default
voice\listen\.venv\Scripts\python.exe voice\listen\listen.py -d 8       # 8s
voice\listen\.venv\Scripts\python.exe voice\listen\listen.py --model small.en
```

Models (downloaded on first use, cached in `~/.cache/huggingface/`):

| Model | Size | Quality | First-run download |
|-------|------|---------|--------------------|
| `tiny.en` | ~75 MB | Rough | ~15s |
| `base.en` ⭐ default | ~150 MB | Good | ~30s |
| `small.en` | ~480 MB | Great | ~90s |
| `medium.en` | ~1.5 GB | Excellent | ~5min |
| `large-v3` | ~3 GB | Best (multilingual) | ~10min |

After the first run, model load takes ~1s and transcription is sub-second on CPU for short clips.

## Phase 2: Push-to-talk + auto-type

Hold a hotkey (F9 by default), speak, release — the transcript types itself into whichever window is focused. So when Claude Code's prompt is focused, your words land right there.

```powershell
voice\listen\.venv\Scripts\python.exe voice\listen\ptt.py
voice\listen\.venv\Scripts\python.exe voice\listen\ptt.py --hotkey f10
voice\listen\.venv\Scripts\python.exe voice\listen\ptt.py --no-type   # print only, don't type
```

**How to use:**
1. Run the command above in a terminal — leave it running.
2. Click into Claude Code's prompt (or any window that takes text input).
3. **Hold F9**, speak, **release**. Watch the transcript appear at your cursor.
4. Press **Esc** to quit the listener.

Flags: `--hotkey` (default `f9`; try `f10`, `space`, `scroll_lock`), `--model` (default `base.en`), `--type-delay` (default `0.18s` — bump it up if your first character gets eaten by the focus shift), `--no-type` (debug: print transcript instead of typing it).

Taps shorter than 200ms are ignored to avoid accidental triggers.

## Setup (first time only)

```powershell
cd voice\listen
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Troubleshooting

- **`mic error`** → run `voice\listen\.venv\Scripts\python.exe -c "import sounddevice; print(sounddevice.query_devices())"` to list devices and confirm Windows sees your mic.
- **Slow first run** → that's the model download. Subsequent runs are fast.
- **Empty transcript** → either silence, or Whisper's VAD filter rejected it. Try a smaller `--model tiny.en` to rule out corruption.

## Why faster-whisper?

It's a CTranslate2 reimplementation of OpenAI's Whisper — same accuracy, ~4x faster on CPU, and runs comfortably on int8 quantization with no GPU. Plays nice with our local-first ethos.
