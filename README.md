# RigGPT

AI-driven ham radio transmission platform for the Icom IC-7610 (and other CI-V compatible radios).

RigGPT is a Flask-based web application that turns a ham radio into an AI broadcast station. It generates speech from language models, synthesizes it with a configurable TTS engine, keys PTT via CI-V serial control, and transmits over the air. It supports live Discord community integration, vector memory, automated media playback, and a multi-agent AI debate mode called Acid Trip.

Built by a ham who wanted to do something deeply stupid with a perfectly good radio.

---

## Features

### Core Radio Control
- CI-V serial control for Icom radios (IC-7610, IC-7300, IC-705, IC-9700, and more)
- PTT keying via CI-V with configurable address and baud rate
- Frequency and mode control from the web UI
- ALSA audio routing to the radio's USB audio codec
- Audio calibration and ALC measurement tools

### AI Transmission
- Multi-turn chat via Ollama (local LLMs), OpenAI, or Google Gemini
- Configurable persona, temperature, and token budget
- AUTO TX mode: every AI response goes straight to air
- INSPIRE, DOSE, and ORACLE modes for generative chaos
- Full AI debug log with verbose trace mode

### Acid Trip Mode
- Two AI agents debate any topic over the air, turn by turn
- Each agent has its own persona, voice, TTS engine, and LLM
- Six mode presets: Sober, Caffeinated, Spicy, Unhinged, Spiritual, Chaos
- Discord Influence: live audience messages steer the debate in real time
- Discord Interact: audience can hijack the conversation mid-trip
- Canon file injection: feed agents source material from local text files
- Per-agent audio FX: reverb, echo, chorus, flanger, pitch, overdrive, bitcrush
- Audience SSE page: live text feed of the debate for Discord viewers
- Scheduled chaos: random wildcard injections during a running trip
- Pre-trip briefing: agents receive a community knowledge brief before turn 0

### Alexa Mode
- Discord-triggered auto-response system
- Monitors the audience channel for a configurable trigger phrase (default: "AI Radio")
- Fires a single sarcastic, rude, funny AI transmission in response
- Configurable model, TTS engine, voice, and token budget
- Live activity log in the AI tab

### Community Memory (Qdrant RAG)
- Ingests Discord channel history into a local Qdrant vector database
- Builds per-user behavioral profiles via LLM (communication style, humor, topics, role)
- Clusters message history into conversation thread summaries
- Injects relevant community context into agent system prompts at runtime
- Three injection layers: community DNA, audience profiles, past thread summaries
- Pre-trip briefing draws on threads, profiles, and running community references
- Delta ingest via cron: only processes new messages, only rebuilds affected profiles
- De-anonymized: stores real display names alongside SHA-256 author hash

### Clips Tab
- Radio automation media player
- Scans a local directory for .wav, .mp3, .ogg, .flac, .aiff, .m4a files
- Click any clip to key PTT and play it over air
- Amazon S3 bucket as optional second source (requires boto3)
- Background poller rescans on a configurable interval
- Cards show format, estimated duration, file size, and source

### TTS Engines
eSpeak · Piper · Edge TTS · Google TTS · OpenAI TTS · ElevenLabs · Speechify · FastKoko (Kokoro)

### Other
- SSTV image transmission (pysstv)
- Waterfall art generator
- Transmission scheduler and beacon
- Full transmission log with playback
- Dub FX tab (Trenchtown) for audio effects on any transmission
- DOCS button: built-in user manual with troubleshooting and API reference
- Keyboard-first UI: numbered tabs, Ctrl+K command palette, Ctrl+. emergency PTT off

---

## Hardware

Tested on:
- **Radio:** Icom IC-7610
- **Radio machine:** Debian 13, x86_64
- **GPU/AI host:** NVIDIA RTX 5070 Ti, running Ollama and Qdrant in Docker
- **Connection:** USB (CI-V serial + USB audio codec)

Should work with any Icom radio that supports CI-V serial control and USB audio.

---

## Architecture

```
Browser (operator UI)
        ↓
Flask app (app.py) — radio machine
        ├── CI-V serial → Icom radio (PTT + frequency control)
        ├── ALSA aplay → USB audio codec → radio TX audio
        ├── TTS engines (local + cloud)
        ├── Discord poller (community monitoring)
        ├── Alexa watcher (trigger phrase detection)
        ├── Clips poller (media file scanner)
        └── Memory client (Qdrant RAG)
                ↓
        Qdrant vector DB (Docker, separate host)
        Ollama LLM inference (Docker, GPU host)
```

---

## Requirements

**Radio machine (Debian):**
- Python 3.11+
- Flask, requests, pyserial, APScheduler, pysstv, sounddevice
- eSpeak-ng (for default TTS)
- alsa-utils

**For Community Memory (separate host recommended):**
- Docker
- Qdrant container
- Ollama container with GPU (`--gpus all`)
- `nomic-embed-text` model (embedding)
- `qwen3:14b` model (profile and thread summarization)
- boto3 (optional, for S3 clip source)

Full dependency list in `requirements.txt`.

---

## Installation

```bash
git clone https://github.com/afitnacode/riggpt.git
cd riggpt
sudo bash INSTALL.sh
```

The install script creates the `riggpt` service user, installs dependencies, sets up the systemd service, and starts the app on port 5000.

After install, open `http://your-radio-machine-ip:5000` in a browser.

Configure your radio connection in the **CONFIG** tab: serial port, CI-V address, baud rate, and audio device.

---

## Community Memory Setup

See the built-in manual (DOCS button in the app) for full setup instructions including Qdrant deployment, ingestion pipeline, cron configuration, and the Qdrant internals deep-dive.

Quick start:
```bash
# Deploy Qdrant and Ollama on your GPU host (docker-compose.yml included in memory/)
# Pull required models
docker exec ollama ollama pull nomic-embed-text
docker exec ollama ollama pull qwen3:14b

# Run full Discord history ingest
export DISCORD_TOKEN="Bot your-token"
export DISCORD_CHANNEL_ID="your-channel-id"
python3 memory/riggpt-ingest.py --full

# Enable in RigGPT: Config → Community Memory → ENABLED
```

---

## Configuration

All settings are stored in `/home/riggpt/app_settings.json`. API keys (Discord bot token, ElevenLabs, OpenAI, Gemini, S3 credentials) are stored separately in `/home/riggpt/api_keys.json` with field-level encryption.

Never commit either of these files. They are in `.gitignore`.

---

## Disclaimer

This project transmits audio over licensed amateur radio frequencies. You are responsible for complying with your local amateur radio regulations including station identification requirements. AI-generated content transmitted over the air must comply with Part 97 (or your jurisdiction's equivalent). The author is not responsible for what your radio says.

---

## License

MIT — do whatever you want with it. A mention or a QSL card would be appreciated.

---

*73 de the machine*
