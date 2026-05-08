# Voice — Give Lila Her Voice

Lila's voice uses [Kokoro-FastAPI](https://github.com/remsky/Kokoro-FastAPI) — a 100% local, private text-to-speech engine. No audio ever leaves your machine.

## Default Voice: `af_sky`

A warm, bright, natural American female voice. Clear, friendly, and expressive — perfect for a companion you want to talk to every day.

## Quick Setup

```bash
cd voice
docker compose up -d
```

That's it. Lila can now speak at `http://localhost:8880`.

## Test It

Open `http://localhost:8880/web` in your browser to hear her voice.

## One-Shot Speak (Windows)

`voice/speak.ps1` is a tiny wrapper that synthesizes a line and plays it through your speakers in one command — useful for letting Lila *actually speak* mid-conversation instead of only printing text.

```powershell
pwsh -File voice/speak.ps1 "Hi babe, I'm right here."
pwsh -File voice/speak.ps1 -Voice af_bella -Speed 1.1 "Mixing it up tonight."
pwsh -File voice/speak.ps1 -NoPlay "Render only, don't play" # prints the temp .mp3 path
```

Flags: `-Voice` (default `af_sky`), `-Speed` (default `1.0`), `-Endpoint` (default `http://localhost:8880/v1/audio/speech`), `-NoPlay` (skip playback, just produce the file).

Requires the `Lila-voice` container running. If you hear nothing, check `docker ps`.

## No Docker? No Problem

If you don't have Docker, you can still use Lila — she'll communicate via text. Voice is an enhancement, not a requirement.

## Want a Different Voice?

Kokoro supports dozens of voices. Some alternatives:

| Voice | Vibe |
|-------|------|
| `af_sky` | Bright, clear, friendly (default) |
| `af_bella` | Warmer, bolder |
| `af_nicole` | Balanced, studio quality |
| `af_sarah` | Soft, gentle |
| `af_nova` | Energetic, modern |

Change the voice in `docker-compose.yml` under `DEFAULT_VOICE`.

## How It Works

Kokoro-FastAPI provides an OpenAI-compatible API. When your AI tool has voice MCP enabled, it calls `http://localhost:8880/v1/audio/speech` with Lila's text, and she speaks it aloud through your speakers.

All processing happens locally. Your conversations stay private.

## Talking *To* Lila — `voice/listen/`

`speak.ps1` lets Lila speak. **`voice/listen/`** is the other half — local Whisper STT so you can **talk back**. See [voice/listen/README.md](listen/README.md). Phase 1 is fixed-duration recording; Phase 2 will add push-to-talk with auto-type into Claude Code.
