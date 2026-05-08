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

## Phase 2 (next): Push-to-talk + auto-type

Hold a hotkey (F9), speak, release — transcript types itself into Claude Code's prompt. Built on top of `pynput`. Coming soon.

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
