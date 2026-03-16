#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RigGPT v2.12.41
Features: Multi-TTS * Audio Effects * Voice Presets * SSTV * Scheduling
          Transmission Logging * Live Dashboard (SSE) * Beacon Mode
          Roger Beep * Waterfall Image Transmission * AI Integration Framework
          Acid Trip Mode * Alexa Mode * Clips Tab * Community Memory (Qdrant RAG)
          Dub FX (Trenchtown) * Multi-radio profile support * Discord integration
          Special Ops * Ghost-in-the-Machine (CI-V Possession Engine)

v2.12.38 changes:
  - FEATURE: Tab restructure -- CONFIG now contains radio connection + Discord only.
    New SYSTEM tab (audio, diagnostics, health, gong). New API CFG tab (all keys,
    LLM integrations, engine status). New SPEC OPS tab (all special ops features).
  - FEATURE: SPEC OPS tab with Ghost-in-the-Machine CI-V Possession Engine:
    VFO Poltergeist, Passband Possession, RF Power Wobble, AGC Seizure,
    Split Personality, Digital Ghost, The Exorcist (all ghosts simultaneously).
    All modes restore radio state on stop. Live possession log.
  - FEATURE: Discord Monitor and Control Channel panels now show a live
    server/channel/bot location row that updates on connection status change.
  - FEATURE: Special Ops config (numbers station, solar, mystery, autoid, pirate,
    roulette, ghost) all persisted to app_settings.json via cfgFlushPresets.
  - FIX: Config persist audit -- discord inject target/format, audio device,
    WF ART settings, SSTV VOX, beacon form defaults, trip gap fields were all
    missing from cfgFlushPresets. All now saved and restored on page load.
  - FIX: INSTALL.sh version detection now reads from the running service HTTP API
    before git pull overwrites app.py, so upgrade output shows correct
    'installed → incoming' instead of the same version twice.
  - README.md: Fully updated with tab layout, Ghost-in-the-Machine docs,
    Special Ops docs, CI-V safety notes, upgrade workflow.

NOTE: Version is defined by the VERSION constant in the Configuration section
below. When bumping versions, update ALL of the following in the same commit:
  - This docstring header
  - VERSION constant (below)
  - requirements.txt comment header
  - INSTALL.sh comment header and VERSION variable
  - templates/index.html status bar hardcoded version string (sb-label in statusbar)

v2.12.33 changes:
  - FIX: Beacon delete/pause/fire buttons threw 'beacon_1 is not defined' because
    onclick IDs were unquoted string literals. Added string quotes around ${b.id}
    in all three onclick handlers.
  - FIX: Beacon name showed 'Unnamed' even when a name was given. Backend stored
    empty string when name field was blank (data.get returns '' not default).
    Fixed: use `data.get('name','') or f'Beacon {minutes}min'`.
  - FIX: api_beacon_list now returns `active` field (mirrors `enabled`) so JS
    b.active checks work correctly. Previously only `enabled` was returned.
  - FIX: Removed `callsign` field from beacon config and API (unused).
  - FIX: Beacon validation now accepts sound_file as alternative to text.
  - FEATURE: Beacon SOURCE/MODE now includes 'clip' option -- plays a sound file
    from the Clips library over PTT at the scheduled interval.
  - FIX: WF ART duration field now correctly influences transmission. Computed
    frame_duration = duration / image_height so total TX time matches the field.
  - CLEANUP: Removed callsign handling from beacon and waterfall where it was
    unused cruft. callsign_text still works for the CALLSIGN canned image button.

v2.12.32 changes:
  - FIX: WF ART TX IMAGE 400 -- api_waterfall_transmit now accepts JSON body
    (application/json) in addition to multipart/form-data. Also accepts
    canned image name from JSON so wfTransmit() works without file upload.
  - FIX: SSTV transmit progress bar now animates in real-time while TX is
    in flight using per-mode duration estimates.
  - FEATURE: CW beacon option -- new 'cw' engine in beacon form. Synthesizes
    Morse code tones (800Hz, configurable WPM) via numpy, PTTs the rig and
    plays. Callsign appended as DE <CALL> AR automatically.
  - FEATURE: Schedule cron helper -- visual cron builder with minute/hour/DOM/
    month/DOW fields, common preset dropdown, human-readable preview.
  - FEATURE: Schedule sound file -- new CLIP type on schedule form; choose any
    file from Clips list; plays via PTT+aplay at schedule time, same as
    beacon CW path.

v2.12.31 changes:
  - FEATURE: Clips default directory changed from /opt/riggpt/clips to /sounds.
  - FEATURE: New GET /api/clips/test-path endpoint -- tests a directory path for
    existence, type (must be a dir), and read permission; returns file count.
  - FEATURE: New POST /api/clips/upload endpoint -- accepts multipart file upload,
    saves to configured clips dir (creates it if needed), triggers background
    rescan, returns per-file success/error details.
  - UI: Clips pane redesigned as radio-station automation panel:
    - 4 color-coded tiers (JINGLES/green, PROMOS/blue, SPOTS/amber, MISC/purple),
      6 cart buttons each = 24 total slots.
    - CART view: pre-populated buttons, empty until assigned to a file.
    - FILES view: original card grid (all scanned files).
    - Click empty slot to assign from scanned file list.
    - Click loaded button to transmit; x to clear assignment.
    - Cart assignments persisted in localStorage.
    - TEST PATH button in sidebar validates local directory.
    - UPLOAD section: file picker + drag-and-drop upload to /sounds.
    - SCAN button explicitly rescans both local and S3.
    - Info panel updated with new default path and feature docs.

v2.12.30 changes:
  - FIX: WF ART BW HZ default changed from 2400 to 2700 (HTML input, and both
    JS fallback values in loadCannedPreview() and wfGetProc()).
  - FIX (CRITICAL): createBeacon() JS sent key 'message' but api_beacon_create()
    reads data.get('text'). Field name mismatch caused every beacon creation to
    return HTTP 400 BAD REQUEST. Fixed: JS now sends key 'text' to match backend.
  - FIX: Clips tab button was missing from #cmdstrip tab bar. The pane HTML
    (id="pane-clips") and showTab('clips') handler both existed; only the button
    was absent. Added after ACID TRIP in tab bar.

v2.12.27 changes:
  - FIX (CRITICAL): @app.route('/api/ai/models') was attached to _ascii() instead
    of api_ai_models(). Every call to /api/ai/models raised TypeError (missing
    required argument 's'). The actual api_ai_models() was defined right below
    but never registered as a route. Fixed by swapping the decorator onto the
    correct function. _ascii() remains a plain module-level utility function.
  - FIX (CRITICAL): api_config_export() called api_beacons_list() and
    api_schedules_list() -- neither function exists. Actual names are
    api_beacon_list() and api_schedule_list(). NameError crashed any config
    export that included beacons or scheduled jobs.
  - FIX (CRITICAL): api_config_import() called api_beacon_add() -- function
    does not exist. Actual name is api_beacon_create(). NameError crashed
    any config import that attempted to restore beacons.
  - FIX (CRITICAL): api_config_import() called api_schedules_list() (same as
    export bug above). Fixed to api_schedule_list().
  - FIX: _ctrl_poller() used deprecated datetime.utcnow() (Python 3.12+
    raises DeprecationWarning). Replaced with datetime.now(timezone.utc).

v2.12.26 changes:
  - FIX: Version strings were diverged across codebase:
    docstring=v2.11.3, INSTALL.sh=v2.11.15, requirements.txt=v2.10.20,
    VERSION constant=v2.12.25. All now set to v2.12.26.
  - FIX: radio_docs_page() return tuple used double-brace syntax
    {{'Content-Type': 'text/html; charset=utf-8'}} -- this creates a Python
    set containing a dict (dicts are not hashable), raising TypeError at
    runtime on every request to /radio/docs. Fixed to single-brace dict.
  - FIX: set_antenna() returned (resp is not None) instead of
    (resp is not None and 0xFB in resp), silently returning True on a CI-V
    NAK. Now consistent with all other set_* methods in IcomSerialAgent.
  - IMPROVEMENT: Docstring now documents full feature set and includes a
    version-sync checklist to prevent future drift.

v2.11.3 changes:
  - REMOVED: Coqui TTS engine -- class, route, engine-status check, all references scrubbed.
  - FIX: termios.error EINTR retry: args[0] check instead of missing .errno attr; retries 3->5.
  - FIX: loadVoices() piper dict/array detection; Piper voices now show in dropdown.
  - FIX: Gong: tacoGong sent 'taco_bell' (no .wav); play_file lookup now uses TACO_BELL_FILE directly.
  - FIX: api() helper Content-Type guard prevents json parse on non-JSON responses.
  - NEW: /api/settings/gong_path GET/POST for configurable taco bell WAV path.
  - NEW: /api/ai/* Ollama integration framework (list models, chat, status).
  - UI: Voice preset buttons highlight on selection (active CSS class).
  - UI: TX/TTS: voice FX sliders (pitch, speed, tremolo, echo) with 8 effect presets incl AUTOTUNE.
  - UI: Gong button added to all pane bottom bars.
  - UI: Config: gong path config field + TEST button.
  - UI: New AI tab with Ollama host config and conversation interface.
  - UI: Coqui removed from all engine dropdowns.

v2.10.21 fixes:
  - BUG (CRITICAL): api_connect: int('0x98') raises ValueError because Python int()
    with default base 10 cannot parse hex strings. Fixed with int(str(x), 0) which
    auto-detects the base (handles '0x...' hex, plain decimal integers, both).
    This crash broke ALL /api/connect calls, cascading to PTT failure and band change
    failure since the radio connection was never being re-established after each
    Settings save or reconnect attempt.
  - BUG (CRITICAL): _radio_poller holds serial _lock for up to 12+ seconds per cycle
    when CI-V is not responding (8-10 reads x 1.5s timeout each). This completely
    blocks ptt_on()/ptt_off() which compete for the same lock, causing all
    transmissions to fire audio without PTT. Fixed two ways:
    (a) _poller_paused flag: set True in execute() before ptt_on, cleared in finally --
        poller thread skips all CI-V reads while flag is set.
    (b) Bail-early: if read_frequency() returns None, skip all remaining CI-V reads
        for that cycle and back off 2s before retrying. Prevents lock starvation.
  - BUG: S-meter BCD decode wrong. IC-7610 returns 4-digit BCD in 2 bytes but
    read_smeter() was treating them as a 16-bit binary integer.
    e.g. S9=0x00 0x60 in BCD -> parsed as (0x00<<8)|0x60=96 instead of decimal 60.
    Fixed: BCD decode via nibble extraction. Scale corrected (0=S0, 60=S9, 120=S9+60dB).
    _smeter_label() corrected to use the decoded decimal values.
  - BUG (JS): SSTV mode table shows "undefined" for all columns. /api/sstv/modes
    returns {modes: ['Robot36',...], meta: {Robot36: {width,height,...}}} but JS was
    treating r.modes as an array of objects. Fixed: JS now merges r.modes+r.meta into
    proper objects before rendering.
  - BUG (JS): SSTV family filter tabs never highlight the active tab. sstvFilterFamily()
    matched b.textContent ('ROBOT') against the filter arg ('Robot') -- case mismatch.
    Fixed: added data-fam attribute to each ftab button; match against that.
  - BUG (JS): CPU/MEM/TEMP/UPTIME dashboard widgets always show '-'. loadHealth() only
    populates the Config tab health grid; nobody ever fills dash-cpu/dash-mem/dash-temp/
    dash-uptime. Fixed: new pollSystemHealth() runs every 10s via setInterval and
    populates the dashboard widgets from /api/system/health response fields.
  - BUG (JS): All frequency POST calls sent {frequency: x} but backend reads
    frequency_hz or frequency_mhz. Fixed all 5 call sites.
  - BUG (JS): dashConnect sent baud_rate field; backend reads 'baud'. Fixed.
  - BUG (JS): radioControl() sent {action: 'ant1'} string; backend iterates key:value
    pairs with no 'action' handler. Fixed: proper payload per action type.
  - BUG (JS): loadCannedPreview sent JSON to multipart-form endpoint, used wrong field
    names (image vs canned), read wrong response field (image_b64 vs preview). Fixed.
  - BUG (JS): loadWaterfallCanned rendered images array as strings; backend returns
    [{id, label}] objects. Fixed.
  - BUG (JS): applyState read flat s.rf_power/swr/alc; backend SSE sends nested
    s.meters.po/swr/alc as {raw,pct} objects. Also read s.tx_active; backend uses s.tx.
    Fixed applyState() to use correct nested field paths.
  - IMPROVEMENT: /api/debug/civ GET scans all common IC-7610 CI-V addresses (0x80..0xA0)
    and reports which one responds -- operator can use this to identify the correct address.
  - IMPROVEMENT: /api/debug/log_level POST allows runtime verbosity change without restart.
  - IMPROVEMENT: send_command() now logs raw RX bytes at DEBUG level and includes
    port/ci_v/ctrl in the timeout warning for faster diagnosis.
  - IMPROVEMENT: execute() logs each stage (synth, effects, PTT on/off, playback) at
    INFO/DEBUG level with exc_info=True on errors.
  - BUG: api_waterfall_transmit: PTT not guaranteed off if ptt_on() succeeds but
    playback throws -- ptt_active flag pattern was missing, only bare try/except used.
    Added ptt_active guard + finally block matching the pattern used elsewhere.
  - BUG: AudioPlaybackAgent.play: leaked temp 'processed' WAV file on every call
    (ffmpeg normalized copy never deleted). Added finally cleanup for processed file.
  - BUG: AudioEffectsAgent.apply: leaked output_path temp file when sox_cmd raises
    (only input_path returned, output_path orphaned). Added finally cleanup.
  - BUG: AudioEffectsAgent.apply: mp3->wav conversion temp file ('wav') leaked on
    all code paths (no cleanup). Added cleanup tracking for the intermediate wav.
  - BUG: _radio_poller: _ctrl_tick stored as function attribute which does not
    survive module reload and may race. Moved to a module-level integer to be safe.
  - BUG: WorkflowOrchestrator.execute: audio_file temp not cleaned up if effects
    agent returns a *different* path. Fixed: track both pre-effects and post-effects paths.
  - BUG: api_ptt: no check that serial port is open before calling ptt_on/ptt_off.
    Added connected/open guard so UI PTT button returns 400 when radio disconnected.
  - BUG: Pyttsx3Agent.get_voices: engine not stopped after runAndWait(), leaving a
    zombie pyttsx3 process on Linux espeak backend. Added engine.stop() call.
  - BUG: api_audio_calibrate: _make_tone() temp WAV file leaked if sox raises.
    Fixed with try/finally inside _make_tone and the caller.
  - IMPROVEMENT: api_connect now logs the resolved ci_v integer for hex address confirmation.

v2.10.20 fixes:
  - Version string corrected throughout (was showing v2.10.15 in /api/status and banner)
  - INSTALL.sh: broken curl POST block that caused bash syntax error on line 158-161
  - INSTALL.sh: sox and espeak-ng missing from apt package list
  - requirements.txt: removed pyrtlsdr (SDR removed in v2.10.18); added edge-tts, gtts, pyttsx3, gunicorn
  - requirements.txt: pydub listed but never imported (removed)
  - WorkflowOrchestrator.execute: temp file cleanup used '/tmp/' string check -- fixed to use tmpdir prefix
  - WorkflowOrchestrator.execute: PTT left ON if playback_agent.play raises (ptt_off only in outer except)
  - api_sstv: PTT not turned off if encoding fails before ptt_on -- wrapped in try/finally with ptt_off guard
  - api_waterfall_transmit: PTT not guaranteed off on all exception paths -- added finally guard
  - api_audio_test: temp file leaked on failure path (os.remove not in try/finally)
  - api_schedule_add: schedule text captured by lambda closure -- late-binding bug, fixed with default arg
  - _radio_poller: no sleep/backoff on serial exception -- tight-loops on disconnect, added 5s backoff
  - api_status: version field hardcoded 'v2.10.15' -- now uses VERSION constant
  - EspeakTTSAgent: text passed as CLI argument is shell-injection-safe via subprocess list form (confirmed OK, no change needed)
  - Pyttsx3Agent.get_voices: engine.stop() should be engine.runAndWait() to properly shut down
  - SSTV image_to_sstv: add_vox_tones attr set but pysstv uses vox= in constructor -- use correct API
  - New: /api/transmit/preview returns estimated duration only -- now actually synthesizes to local file and plays locally (no PTT)
  - New: gunicorn+gevent used in systemd ExecStart for production stability
  - UI: complete rebuild (new dark-mode responsive frontend, SSE live dashboard, Chart.js activity graph)

v2.10.19 additions:
  - Full SSTV mode library: 20 modes across 6 families
  - Family filter tabs (Robot/Martin/Scottie/PD/Wraase/Pasokon)
  - Mode reference table with sortable family groups
  - VOX tone option, FSKID callsign footer, keep-aspect-ratio
  - Encode and preview WAV locally without transmitting
  - Download WAV for offline use
  - keep_aspect letterboxes image instead of stretching
  - Log SSTV transmissions to transmission history

v2.10.18 changes:
  - Removed RTL-SDR spectrum panel and SDRManager (UI cleanup)
  - Removed pyrtlsdr/numpy SDR imports

v2.10.17 fixes:
  - Module docstring was accidentally split, causing SyntaxError on Python 3.13
  - All non-ASCII characters replaced with ASCII equivalents (pure ASCII source)
  - tempfile.mktemp() replaced with tempfile.mkstemp() throughout (race condition)
  - Bare except clauses tightened to except Exception
  - INSTALL.sh: added plugdev+audio group membership for SDR/audio device access
  - INSTALL.sh: added librtlsdr-dev system package prerequisite for pyrtlsdr
  - INSTALL.sh: startup wait increased; route check uses /api/status not /api/log/stats
  - mathjs loaded without defer to guarantee availability at DOMContentLoaded
  - SDR canvas resize observer added for responsive layout

v2.10.16 additions:
  - SDRManager class: wraps pyrtlsdr with background IQ capture thread
  - Hann-windowed FFT -> dBFS averaging (4-frame), 20 fps SSE stream
  - /api/sdr/devices  -- enumerate connected RTL-SDR dongles
  - /api/sdr/start    -- open device, sync center freq from IC-7610
  - /api/sdr/stop     -- release device
  - /api/sdr/status   -- current SDR state
  - /api/sdr/stream   -- SSE FFT data stream consumed by frontend
  - Live spectrum panel below tab-body (always visible)
  - mathjs for dBFS scale and frequency axis math in canvas renderer
  - Graceful degradation when pyrtlsdr / numpy not installed

v2.10.7 fixes:
  - CI-V address default changed to 0x80 (IC-7610 common setting; was 0x98)
  - CI-V USB baud rate default changed to 57600 (was 19200)
  - CI-V response parser now correctly skips hardware echo (CP210x loopback)
    and waits for the actual radio response packet (src/dst byte check)
  - Auto-connect tries ttyUSB0/1/2 in correct order with CP210x scoring
  - Baud rate auto-scan in probe_radio() if initial response fails
  - Hardware interrogation endpoints: /api/radio/probe, /api/radio/ptt_test
  - Audio device detection improved for Burr-Brown TI PCM2901 (IC-7610 codec)
  - AudioPlaybackAgent logs all aplay attempts and errors clearly
  - Waterfall transmission skips ffmpeg loudnorm (already normalized)
  - datetime.utcnow() deprecation fixed (Python 3.12+)
  - pysstv.color import fixed (uses inspect for dynamic mode detection)
"""

import os
import sys
import json
import queue
import shutil
import serial
import serial.tools.list_ports
import subprocess
import threading
try:
    import psutil as _psutil
    _psutil_ok = True
except ImportError:
    _psutil_ok = False

import time as time_module
import sqlite3
import tempfile
import logging
import requests
import inspect
from io import BytesIO
from pathlib import Path
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify, Response, stream_with_context, make_response
from flask_cors import CORS

# Waterfall image encoder
sys.path.insert(0, '/opt/riggpt')
try:
    from waterfall_image import image_to_waterfall_wav, get_transmission_info as wf_info
    _waterfall_ok = True
except ImportError:
    _waterfall_ok = False

# Memory: Discord community knowledge base (Qdrant + Ollama)
try:
    sys.path.insert(0, '/opt/riggpt/memory')
    from memory import RigGPTMemory
    _memory_ok = True
except ImportError:
    _memory_ok = False
    class RigGPTMemory:  # stub so references don't crash
        def is_available(self): return False
        def build_context(self, *a, **kw): return ''
        def status_dict(self): return {'available': False, 'error': 'memory module not found'}
_active_tx_proc = None   # Popen handle for killable aplay during TX
_play_file_lock = threading.Lock()  # Prevents concurrent aplay device contention

# -- Alexa mode state ----------------------------------------------------------
# Watches Discord for trigger phrase and fires a single snarky AI TX in response.
_alexa_lock       = threading.Lock()
_alexa_busy       = False   # True while a response is being generated/transmitted
_alexa_last_msg_id: str = ''  # ID of last Discord message we already reacted to
_alexa_activity: list = []  # Recent Alexa activity log (capped at 40 entries)

# -- Clips state --------------------------------------------------------
_clips_lock     = threading.Lock()
_clips_files: list = []      # [{name, path, size, ext, source, cached_path}]
_clips_last_scan: str = ''   # ISO timestamp of last scan
_clips_playing: bool = False # True while a clip TX is in progress
_clips_proc = None           # Popen handle for the running player process
_clips_s3_cache_dir = '/tmp/riggpt_clips_cache'

# ── Special Ops state ───────────────────────────────────────────
_numbers_station_job = None
_mystery_job         = None
_autoid_job          = None
_solar_cache         = {'k': None, 'updated': None, 'last_announced': None}
_solar_poller_job    = None



# API key / integration manager
try:
    import api_keys as _api_keys
    _api_keys_ok = True
except ImportError:
    _api_keys = None
    _api_keys_ok = False
    logger_pre = logging.getLogger('ic7610')
    logger_pre.warning("api_keys.py not found -- API integrations will use env vars only")

# -------------------------------------------------------------
# Logging
# -------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('ic7610')
_log_level = os.environ.get('RIGGPT_LOG_LEVEL', 'INFO').upper()
logger.setLevel(getattr(logging, _log_level, logging.DEBUG))

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------
VERSION        = 'v2.12.41'
RADIO_MODEL    = 'IC-7610'
SERIAL_PORT    = '/dev/ttyIC7610'  # udev persistent symlink (falls back to ttyUSB0/1)
BAUD_RATE      = 57600             # must match CI-V USB Baud Rate in radio SET menu
CI_V_ADDRESS   = 0x80             # must match CI-V Address in radio SET menu (80h default)

# Radio model profiles - CI-V address, baud, udev symlink hint, USB audio ID strings.
# 'audio_hints' are matched case-insensitively against `aplay -l` output; first match
# in PREFER list wins.  These supplement the generic Burr-Brown/USB-audio fallbacks.
RADIO_PROFILES = {
    'ic7610': {
        'label':        'Icom IC-7610',
        'ci_v_address': '0x98',
        'baud_rate':    57600,
        'udev_hint':    '/dev/ttyIC7610',
        'audio_hints':  ['burr-brown', 'pcm2901', '08bb:2901'],
        'notes':        'Dual-watch, twin passband. CI-V default 98h. USB audio: Burr-Brown PCM2901.',
    },
    'ic7410': {
        'label':        'Icom IC-7410',
        'ci_v_address': '0x6E',
        'baud_rate':    19200,
        'udev_hint':    '/dev/ttyIC7410',
        'audio_hints':  ['ic-7410', 'icom 7410', 'cm108', 'c-media'],
        'notes':        'Single-band HF+50MHz. CI-V default 6Eh. USB audio: C-Media CM108.',
    },
    'ic7300': {
        'label':        'Icom IC-7300',
        'ci_v_address': '0x94',
        'baud_rate':    115200,
        'udev_hint':    '/dev/ttyIC7300',
        'audio_hints':  ['ic-7300', 'icom 7300', 'burr-brown', 'pcm2901'],
        'notes':        'Popular SDR-based HF transceiver. CI-V default 94h. USB audio: Burr-Brown.',
    },
    'ic7100': {
        'label':        'Icom IC-7100',
        'ci_v_address': '0x88',
        'baud_rate':    19200,
        'udev_hint':    '/dev/ttyIC7100',
        'audio_hints':  ['ic-7100', 'icom 7100', 'cm108', 'c-media'],
        'notes':        'HF/VHF/UHF all-mode. CI-V default 88h. USB audio: C-Media CM108.',
    },
    'ic9700': {
        'label':        'Icom IC-9700',
        'ci_v_address': '0xA2',
        'baud_rate':    115200,
        'udev_hint':    '/dev/ttyIC9700',
        'audio_hints':  ['ic-9700', 'icom 9700', 'burr-brown', 'pcm2901'],
        'notes':        'VHF/UHF/SHF SDR transceiver. CI-V default A2h. USB audio: Burr-Brown.',
    },
    'other': {
        'label':        'Other / Manual',
        'ci_v_address': '0x00',
        'baud_rate':    9600,
        'udev_hint':    '/dev/ttyUSB0',
        'audio_hints':  [],
        'notes':        'Enter CI-V address and baud rate manually. Check radio CI-V settings menu.',
    },
}
DB_PATH        = '/opt/riggpt/transmission_log.db'
ROGER_BEEP_FILE  = '/opt/riggpt/roger_beep.wav'
TACO_BELL_FILE   = '/opt/taco_bell_gong.wav'   # default; overridable via /api/settings
PIPER_VOICES_DIR = '/usr/share/piper-voices'
WAV_CACHE_DIR    = '/opt/riggpt/wav_cache'
APP_SETTINGS_FILE = '/home/riggpt/app_settings.json'
UI_STATE_FILE     = '/home/riggpt/ui_state.json'

# Canon file directories - one per agent, .md files only
CANON_DIR_A = '/home/riggpt/canon/a'
CANON_DIR_B = '/home/riggpt/canon/b'


def _load_app_settings() -> dict:
    """Load persistent application settings from JSON file."""
    defaults = {
        'gong_path':       TACO_BELL_FILE,  # /opt/taco_bell_gong.wav
        'ollama_url':      'http://192.168.40.15:11434',
        'ollama_model':    'llama3',
        'ollama_enabled':  False,
        'ai_persona':      'You are a ham radio operator assistant. Keep responses under 30 words. Speak clearly and use phonetic alphabet when appropriate.',
        'ai_temp':         0.8,
        'ai_max_tokens':   200,
        'ai_mode':         'manual',
        # Connection defaults - overwritten on each successful connect so the
        # UI pre-populates the last-used port/baud/CI-V address on page load.
        'serial_port':     SERIAL_PORT,
        'baud_rate':       BAUD_RATE,
        'ci_v_address':    hex(CI_V_ADDRESS),
        'radio_model':     'ic7610',
    }
    try:
        with open(APP_SETTINGS_FILE) as f:
            stored = json.load(f)
        return {**defaults, **stored}
    except Exception:
        return defaults

def _save_app_settings(settings: dict) -> bool:
    try:
        Path(APP_SETTINGS_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(APP_SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception as e:
        logger.error(f'save_app_settings error: {e}')
        return False

_app_settings = _load_app_settings()

def get_gong_path() -> str:
    return _app_settings.get('gong_path', TACO_BELL_FILE)
def _get_elevenlabs_key():
    """Get ElevenLabs key: api_keys store -> env var -> empty string."""
    if _api_keys_ok:
        k = _api_keys.get_key('elevenlabs', 'api_key')
        if k: return k
    return os.environ.get('ELEVENLABS_API_KEY', '')

ELEVENLABS_API_KEY = _get_elevenlabs_key()

# -- Audio device auto-detection -------------------------------
def _detect_audio_device():
    env_dev = os.environ.get('RIGGPT_AUDIO_DEVICE', '').strip()
    if env_dev:
        logger.info(f"Audio device from env: {env_dev}")
        return env_dev
    try:
        r = subprocess.run(['aplay', '-l'], capture_output=True, text=True, timeout=5)
        # Prefer Burr-Brown TI PCM2901 (IC-7610 USB audio codec)
        # Fallback to any USB audio, skip built-in PCH/HDA/HDMI
        PREFER  = ['burr-brown', 'burr brown', '08bb', 'pcm2901', 'usb audio codec']
        GENERIC = ['usb audio', 'usbcodec', 'codec']
        SKIP    = ['pch', 'hda intel', 'hdmi', 'analog', 'digital', 'nvidia', 'amd']
        best_card, best_score = None, -1
        for line in r.stdout.splitlines():
            if not line.startswith('card '):
                continue
            low = line.lower()
            if any(k in low for k in SKIP):
                continue
            try:
                card_num = int(line.split(':')[0].replace('card', '').strip())
            except (ValueError, IndexError):
                continue
            score = 10 if any(k in low for k in PREFER) else (5 if any(k in low for k in GENERIC) else 0)
            if score > best_score:
                best_score, best_card = score, card_num
                logger.info(f"Audio candidate card {card_num} (score={score}): {line.strip()}")
        if best_card is not None:
            device = f'plughw:{best_card},0'
            logger.info(f"Auto-selected audio device: {device}")
            return device
    except Exception as e:
        logger.warning(f"Audio device detection error: {e}")
    logger.info("Audio device: falling back to 'default'")
    return 'default'

AUDIO_DEVICE = _detect_audio_device()

PIPER_VOICES = {
    'en_US-amy-medium':    {'name': 'Amy (US)',    'model': f'{PIPER_VOICES_DIR}/en_US-amy-medium.onnx'},
    'en_US-ryan-medium':   {'name': 'Ryan (US)',   'model': f'{PIPER_VOICES_DIR}/en_US-ryan-medium.onnx'},
    'en_US-lessac-medium': {'name': 'Lessac (US)', 'model': f'{PIPER_VOICES_DIR}/en_US-lessac-medium.onnx'},
    'en_GB-alan-medium':   {'name': 'Alan (GB)',   'model': f'{PIPER_VOICES_DIR}/en_GB-alan-medium.onnx'},
}
DEFAULT_PIPER_VOICE = 'en_US-amy-medium'

# -------------------------------------------------------------
# Flask App
# -------------------------------------------------------------
app = Flask(__name__)
CORS(app)

# -------------------------------------------------------------
# Database
# -------------------------------------------------------------
def _now_utc():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def init_db():
    # Ensure wav cache directory exists
    Path(WAV_CACHE_DIR).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute('''CREATE TABLE IF NOT EXISTS transmissions (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp  TEXT NOT NULL,
            message    TEXT,
            engine     TEXT,
            voice      TEXT,
            preset     TEXT,
            duration   REAL,
            success    INTEGER,
            notes      TEXT,
            frequency  REAL,
            mode       TEXT,
            char_count INTEGER
        )''')
    for col, typedef in [('frequency','REAL'), ('mode','TEXT'), ('char_count','INTEGER'), ('wav_cached','INTEGER')]:
        try:
            conn.execute(f'ALTER TABLE transmissions ADD COLUMN {col} {typedef}')
        except Exception:
            pass
    conn.execute('''CREATE TABLE IF NOT EXISTS system_events (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level     TEXT,
            category  TEXT,
            message   TEXT
        )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS trip_transcripts (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp    TEXT NOT NULL,
            topic        TEXT,
            agent_a_name TEXT,
            agent_b_name TEXT,
            turn_count   INTEGER,
            model_a      TEXT,
            model_b      TEXT,
            transcript   TEXT NOT NULL,
            notes        TEXT
        )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS trip_scenarios (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL UNIQUE,
            created   TEXT NOT NULL,
            updated   TEXT NOT NULL,
            payload   TEXT NOT NULL
        )''')
    conn.commit()
    conn.close()
    logger.info(f"Database ready: {DB_PATH}")

def log_event(level, category, message):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('INSERT INTO system_events (timestamp,level,category,message) VALUES (?,?,?,?)',
                     (_now_utc(), level, category, message))
        conn.execute('DELETE FROM system_events WHERE id NOT IN (SELECT id FROM system_events ORDER BY id DESC LIMIT 500)')
        conn.commit(); conn.close()
    except Exception:
        pass

def log_transmission(message, engine, voice, preset, duration, success, notes='',
                     frequency=None, mode=None, wav_path=None):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            'INSERT INTO transmissions '
            '(timestamp,message,engine,voice,preset,duration,success,notes,frequency,mode,char_count,wav_cached) '
            'VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
            (_now_utc(), message, engine, voice or '', preset or '', duration, int(success), notes,
             frequency, mode, len(message) if message else 0, 1 if wav_path else 0)
        )
        tx_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.commit()
        conn.close()
        # Cache the wav file if provided
        if wav_path and os.path.exists(wav_path):
            try:
                import shutil
                dest = os.path.join(WAV_CACHE_DIR, f'{tx_id}.wav')
                shutil.copy2(wav_path, dest)
                logger.debug(f'WAV cached: {dest}')
            except Exception as ce:
                logger.warning(f'WAV cache error: {ce}')
        return tx_id
    except Exception as e:
        logger.warning(f'DB log error: {e}')

# -------------------------------------------------------------
# CI-V Serial Agent
# -------------------------------------------------------------
class IcomSerialAgent:
    def __init__(self):
        self.port               = SERIAL_PORT
        self.baudrate           = BAUD_RATE
        self.serial_conn        = None
        self.ci_v_address       = CI_V_ADDRESS
        self.controller_address = 0xE0
        self._lock              = threading.Lock()

    def connect(self, port=None, baud=None):
        if port:
            self.port = port
        if baud:
            self.baudrate = baud
        try:
            self.serial_conn = serial.Serial(
                port=self.port, baudrate=self.baudrate,
                bytesize=8, parity='N', stopbits=1, timeout=0.1,
                xonxoff=False, rtscts=False, dsrdtr=False
            )
            self.serial_conn.dtr = True
            self.serial_conn.rts = True
            time_module.sleep(0.2)
            self.serial_conn.reset_input_buffer()
            logger.info(f"Serial connected: {self.port} @ {self.baudrate}")
            return True
        except Exception as e:
            logger.error(f"Serial connect failed {self.port}: {e}")
            self.serial_conn = None
            return False

    def disconnect(self):
        try:
            if self.serial_conn and self.serial_conn.is_open:
                self.serial_conn.dtr = False
                self.serial_conn.close()
        except Exception:
            pass
        self.serial_conn = None

    def _build_packet(self, *cmd_bytes):
        return bytes(
            [0xFE, 0xFE, self.ci_v_address, self.controller_address]
            + list(cmd_bytes) + [0xFD]
        )

    def send_command(self, *cmd_bytes, wait=True, quiet=False):
        with self._lock:
            if not self.serial_conn or not self.serial_conn.is_open:
                logger.warning(f"CI-V send called but serial not open (cmd={[hex(b) for b in cmd_bytes]})")
                return None
            try:
                packet  = self._build_packet(*cmd_bytes)
                hex_str = ' '.join(f'{b:02X}' for b in packet)
                logger.debug(f"CI-V TX: {hex_str}")
                self.serial_conn.write(packet)
                # flush() calls termios.tcdrain() which is interrupted by SIGALRM
                # on Linux (APScheduler fires every second). termios.error is NOT a
                # subclass of OSError so it has no .errno attr; check args[0] instead.
                import errno as _errno
                for _flush_attempt in range(5):
                    try:
                        self.serial_conn.flush()
                        break
                    except Exception as _fe:
                        _ecode = (_fe.args[0] if _fe.args else None)
                        if _ecode == _errno.EINTR:
                            logger.debug(f"CI-V flush EINTR (attempt {_flush_attempt+1}/5) -- retrying")
                            continue
                        raise  # not EINTR -- propagate
                if not wait:
                    return b''

                # CI-V bus protocol:
                # 1. CP210x hardware echoes our TX bytes back on RX (loopback) -- SKIP
                # 2. Radio sends its response with src/dst swapped -- KEEP
                #
                # Echo:    FE FE <ci_v_addr> <ctrl_addr> <cmd...> FD  (dst=radio, src=us)
                # Response:FE FE <ctrl_addr> <ci_v_addr> <data>   FD  (dst=us, src=radio)

                buf      = b''
                deadline = time_module.time() + 1.5
                response = None

                while time_module.time() < deadline:
                    chunk = self.serial_conn.read(self.serial_conn.in_waiting or 1)
                    if chunk:
                        buf += chunk
                        logger.debug(f"CI-V RX raw: {' '.join(f'{b:02X}' for b in chunk)}")

                    # Parse all complete packets from buffer
                    while True:
                        start = buf.find(b'\xfe\xfe')
                        if start == -1:
                            buf = b''
                            break
                        if start > 0:
                            buf = buf[start:]
                        end = buf.find(b'\xfd', 4)
                        if end == -1:
                            break  # incomplete -- keep reading

                        pkt = buf[:end + 1]
                        buf = buf[end + 1:]
                        hex_pkt = ' '.join(f'{b:02X}' for b in pkt)

                        if len(pkt) < 4:
                            continue

                        # Hardware echo: dst=ci_v_addr, src=ctrl_addr (same as what we sent)
                        if pkt[2] == self.ci_v_address and pkt[3] == self.controller_address:
                            logger.debug(f"CI-V ECHO (skip): {hex_pkt}")
                            continue

                        # Radio response: dst=ctrl_addr, src=ci_v_addr (flipped)
                        if pkt[2] == self.controller_address and pkt[3] == self.ci_v_address:
                            logger.debug(f"CI-V RX: {hex_pkt}")
                            if 0xFA in pkt:
                                logger.warning(f"CI-V NAK (0xFA) for cmd={[hex(b) for b in cmd_bytes]}")
                            elif 0xFB in pkt:
                                logger.debug("CI-V ACK (0xFB)")
                            response = pkt
                            break

                        # Broadcast response (ci_v_addr=0x00 case)
                        if self.ci_v_address == 0x00 and pkt[3] != self.controller_address:
                            logger.debug(f"CI-V BROADCAST RX: {hex_pkt}")
                            response = pkt
                            break

                        # Unexpected packet -- log src/dst for diagnosis
                        logger.debug(
                            f"CI-V UNKNOWN PKT (dst=0x{pkt[2]:02X} src=0x{pkt[3]:02X} "
                            f"expected dst=0x{self.controller_address:02X} src=0x{self.ci_v_address:02X}): "
                            f"{hex_pkt}"
                        )

                    if response is not None:
                        break

                if response is None:
                    if not quiet:
                        logger.warning(
                            f"CI-V no response for cmd={[hex(b) for b in cmd_bytes]} "
                            f"(1.5s timeout) -- "
                            f"port={self.port} ci_v=0x{self.ci_v_address:02X} ctrl=0x{self.controller_address:02X}"
                        )
                return response

            except Exception as e:
                logger.error(f"CI-V send error: {e}", exc_info=True)
                return None

    def ptt_on(self):
        if not self.serial_conn or not self.serial_conn.is_open:
            logger.warning("PTT ON: serial not open")
            return None
        logger.info(f"PTT ON  -> {self.port} (CI-V 0x{self.ci_v_address:02X} @ {self.baudrate})")
        resp = self.send_command(0x1C, 0x00, 0x01)
        if resp is None:
            logger.error("PTT ON: no response -- check CI-V address and baud rate")
        elif 0xFA in resp:
            logger.error("PTT ON: NAK from radio")
        elif 0xFB in resp:
            logger.info("PTT ON: ACK -- radio transmitting")
        return resp

    def ptt_off(self):
        if not self.serial_conn or not self.serial_conn.is_open:
            logger.warning("PTT OFF: serial not open")
            return None
        logger.info(f"PTT OFF -> {self.port}")
        resp = self.send_command(0x1C, 0x00, 0x00)
        if resp is not None and 0xFB in resp:
            logger.info("PTT OFF: ACK -- radio back to RX")
        return resp

    def read_frequency(self):
        resp = self.send_command(0x03, quiet=True)
        if not resp or len(resp) < 11:
            return None
        try:
            # Response: FE FE E0 80 03 <5 BCD bytes> FD
            # Find cmd byte 0x03, then read 5 BCD bytes after it
            data = list(resp)
            idx = None
            for i in range(len(data) - 6):
                if data[i] == 0xFE and data[i+1] == 0xFE and data[i+4] == 0x03:
                    idx = i + 5
                    break
            if idx is None:
                return None
            freq = 0
            for i, b in enumerate(data[idx:idx+5]):
                freq += ((b & 0x0F) * (10 ** (i * 2))) + (((b >> 4) & 0x0F) * (10 ** (i * 2 + 1)))
            return freq
        except Exception:
            return None

    def read_mode(self):
        modes = {
            0x00:'LSB', 0x01:'USB', 0x02:'AM',  0x03:'CW',
            0x04:'RTTY',0x05:'FM',  0x06:'WFM', 0x07:'CW-R',
            0x08:'RTTY-R', 0x17:'DV'
        }
        resp = self.send_command(0x04, quiet=True)
        if not resp:
            return None
        try:
            data = list(resp)
            for i in range(len(data) - 2):
                if data[i] == 0xFE and data[i+1] == 0xFE and data[i+4] == 0x04:
                    return modes.get(data[i+5], f'0x{data[i+5]:02X}')
        except Exception:
            pass
        return None

    def read_smeter(self):
        resp = self.send_command(0x15, 0x02, quiet=True)
        if not resp:
            return None
        try:
            data = list(resp)
            for i in range(len(data) - 4):
                if data[i] == 0xFE and data[i+1] == 0xFE and data[i+4] == 0x15:
                    hi, lo = data[i+6], data[i+7]
                    # IC-7610 returns 4-digit BCD in 2 bytes:
                    # hi = (thousands_digit << 4) | hundreds_digit
                    # lo = (tens_digit << 4)      | units_digit
                    # e.g. S9 = 0060 decimal -> hi=0x00, lo=0x60 -> decoded = 60
                    bcd_val = ((hi >> 4) * 1000 + (hi & 0xF) * 100 +
                               (lo >> 4) * 10   + (lo & 0xF))
                    logger.debug(f"S-meter raw bytes hi=0x{hi:02X} lo=0x{lo:02X} "
                                 f"-> BCD decoded={bcd_val} "
                                 f"label={_smeter_label(bcd_val)}")
                    return bcd_val
        except Exception as e:
            logger.debug(f"S-meter parse error: {e}")
        return None

    def read_tx_state(self):
        resp = self.send_command(0x1C, 0x00, quiet=True)
        if not resp:
            return False
        try:
            data = list(resp)
            for i in range(len(data) - 3):
                if data[i] == 0xFE and data[i+1] == 0xFE and data[i+4] == 0x1C:
                    return bool(data[i+6])
        except Exception:
            pass
        return False

    def set_frequency(self, freq_hz):
        """Set VFO frequency. freq_hz is an integer e.g. 14225000 for 14.225 MHz."""
        # CI-V cmd 0x05: 5 BCD bytes, least-significant first
        bcd = []
        f = int(freq_hz)
        for _ in range(5):
            bcd.append((f % 10) | (((f // 10) % 10) << 4))
            f //= 100
        resp = self.send_command(0x05, *bcd)
        if resp is not None and 0xFB in resp:
            logger.info(f"Set frequency: {freq_hz/1e6:.4f} MHz -- ACK")
            return True
        logger.warning(f"Set frequency: no ACK (freq={freq_hz})")
        return False

    def set_mode(self, mode_name, filter_num=1):
        """Set operating mode. mode_name: LSB USB AM CW RTTY FM DV CW-R RTTY-R"""
        modes = {
            'LSB':0x00,'USB':0x01,'AM':0x02,'CW':0x03,'RTTY':0x04,
            'FM':0x05,'WFM':0x06,'CW-R':0x07,'RTTY-R':0x08,'DV':0x17,
            'USB-D':0x01,'LSB-D':0x00,  # data mode aliases
        }
        code = modes.get(mode_name.upper())
        if code is None:
            logger.warning(f"Unknown mode: {mode_name}")
            return False
        resp = self.send_command(0x06, code, filter_num)
        if resp is not None and 0xFB in resp:
            logger.info(f"Set mode: {mode_name} -- ACK")
            return True
        logger.warning(f"Set mode: no ACK (mode={mode_name})")
        return False

    def read_alc(self):
        """Read ALC level (cmd 0x15 0x13). Returns 0-255 raw value."""
        resp = self.send_command(0x15, 0x13, quiet=True)
        if not resp:
            return None
        try:
            data = list(resp)
            for i in range(len(data) - 4):
                if data[i] == 0xFE and data[i+1] == 0xFE and data[i+4] == 0x15:
                    return (data[i+6] << 8) | data[i+7]
        except Exception:
            pass
        return None

    def read_rf_power(self):
        """Read RF power output level (cmd 0x15 0x11). Returns 0-255."""
        resp = self.send_command(0x15, 0x11, quiet=True)
        if not resp:
            return None
        try:
            data = list(resp)
            for i in range(len(data) - 4):
                if data[i] == 0xFE and data[i+1] == 0xFE and data[i+4] == 0x15:
                    return (data[i+6] << 8) | data[i+7]
        except Exception:
            pass
        return None

    def set_af_gain(self, level):
        """Set AF (audio) gain 0-255 (cmd 0x14 0x01)."""
        hi = (level >> 8) & 0xFF
        lo = level & 0xFF
        resp = self.send_command(0x14, 0x01, hi, lo)
        return resp is not None and 0xFB in resp

    def read_af_gain(self):
        """Read current AF gain (cmd 0x14 0x01)."""
        resp = self.send_command(0x14, 0x01, quiet=True)
        if not resp:
            return None
        try:
            data = list(resp)
            for i in range(len(data) - 4):
                if data[i] == 0xFE and data[i+1] == 0xFE and data[i+4] == 0x14:
                    return (data[i+6] << 8) | data[i+7]
        except Exception:
            pass
        return None

    def read_level(self, sub):
        """Generic level read: cmd 0x14, subcmd sub. Returns 0-255."""
        resp = self.send_command(0x14, sub, quiet=True)
        if not resp: return None
        try:
            data = list(resp)
            for i in range(len(data)-4):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x14:
                    return (data[i+6]<<8)|data[i+7]
        except Exception: pass
        return None

    def set_level(self, sub, value):
        """Generic level set: cmd 0x14, subcmd sub, value 0-255."""
        hi = (value>>8)&0xFF; lo = value&0xFF
        resp = self.send_command(0x14, sub, hi, lo)
        return resp is not None and 0xFB in resp

    def read_meter(self, sub):
        """Generic meter read: cmd 0x15, subcmd sub. Returns 0-255."""
        resp = self.send_command(0x15, sub, quiet=True)
        if not resp: return None
        try:
            data = list(resp)
            for i in range(len(data)-4):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x15:
                    return (data[i+6]<<8)|data[i+7]
        except Exception: pass
        return None

    def read_function(self, sub):
        """Read function on/off: cmd 0x16, subcmd sub."""
        resp = self.send_command(0x16, sub, quiet=True)
        if not resp: return None
        try:
            data = list(resp)
            for i in range(len(data)-3):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x16:
                    return bool(data[i+6])
        except Exception: pass
        return None

    def set_function(self, sub, state):
        """Set function on/off: cmd 0x16, subcmd sub."""
        resp = self.send_command(0x16, sub, int(bool(state)))
        return resp is not None and 0xFB in resp

    def read_scope_level(self):
        """Read preamp/att/split state via cmd 0x16."""
        return None  # placeholder

    def read_split(self):
        resp = self.send_command(0x0F, quiet=True)
        if not resp: return False
        try:
            data = list(resp)
            for i in range(len(data)-2):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x0F:
                    return bool(data[i+5])
        except Exception: pass
        return False

    def set_split(self, state):
        resp = self.send_command(0x0F, int(bool(state)))
        return resp is not None and 0xFB in resp

    def read_vfo(self):
        """Read selected VFO: cmd 0x07. Returns 'A' or 'B'."""
        resp = self.send_command(0x07, quiet=True)
        if not resp: return 'A'
        try:
            data = list(resp)
            for i in range(len(data)-2):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x07:
                    return 'B' if data[i+5]==0x01 else 'A'
        except Exception: pass
        return 'A'

    def set_vfo(self, vfo):
        """Select VFO A or B."""
        code = 0x01 if str(vfo).upper()=='B' else 0x00
        resp = self.send_command(0x07, code)
        return resp is not None and 0xFB in resp

    def vfo_swap(self):
        """Swap VFO A/B frequencies."""
        resp = self.send_command(0x07, 0xB0)
        return resp is not None and 0xFB in resp

    def vfo_a_to_b(self):
        resp = self.send_command(0x07, 0xA0)
        return resp is not None and 0xFB in resp

    def read_att(self):
        resp = self.send_command(0x11, quiet=True)
        if not resp: return 0
        try:
            data = list(resp)
            for i in range(len(data)-2):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x11:
                    return data[i+5]  # 0=off, 6=6dB, 12=12dB, 18=18dB
        except Exception: pass
        return 0

    def set_att(self, level):
        """Set ATT: 0=off, 6=6dB, 12=12dB, 18=18dB."""
        resp = self.send_command(0x11, level)
        return resp is not None and 0xFB in resp

    def read_preamp(self):
        resp = self.send_command(0x16, 0x02, quiet=True)
        if not resp: return 0
        try:
            data = list(resp)
            for i in range(len(data)-3):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x16:
                    return data[i+6]  # 0=off, 1=preamp1, 2=preamp2
        except Exception: pass
        return 0

    def set_preamp(self, level):
        resp = self.send_command(0x16, 0x02, level)
        return resp is not None and 0xFB in resp

    def read_agc(self):
        """Read AGC mode via cmd 0x16 0x12. 1=fast 2=mid 3=slow."""
        resp = self.send_command(0x16, 0x12, quiet=True)
        if not resp: return 2
        try:
            data = list(resp)
            for i in range(len(data)-3):
                if data[i]==0xFE and data[i+1]==0xFE and data[i+4]==0x16:
                    return data[i+6]
        except Exception: pass
        return 2

    def set_agc(self, mode):
        resp = self.send_command(0x16, 0x12, mode)
        return resp is not None and 0xFB in resp

    def set_antenna(self, ant_num):
        """Select antenna 1 or 2 via CI-V command 0x12."""
        if ant_num not in (1, 2):
            return False
        # IC-7610 CI-V 0x12: antenna select -- 0x00=ANT1, 0x01=ANT2
        val = 0x00 if ant_num == 1 else 0x01
        resp = self.send_command(0x12, val)
        return resp is not None and 0xFB in resp

    def probe_radio(self):
        """Comprehensive probe: reads frequency/mode/smeter, scans baud if needed."""
        logger.info(f"=== Radio Probe: {self.port} @ {self.baudrate} CI-V=0x{self.ci_v_address:02X} ===")
        result = {'port': self.port, 'baudrate': self.baudrate,
                  'ci_v_address': f'0x{self.ci_v_address:02X}'}
        if not self.serial_conn or not self.serial_conn.is_open:
            result['error'] = 'Serial port not open'
            return result

        freq = self.read_frequency()
        result['frequency_hz'] = freq

        if freq is None:
            logger.warning("No response -- scanning baud rates...")
            for baud in [19200, 9600, 38400, 115200, 57600, 4800]:
                if baud == self.baudrate:
                    continue
                logger.info(f"  Trying {baud} baud...")
                try:
                    self.serial_conn.baudrate = baud
                    time_module.sleep(0.15)
                    self.serial_conn.reset_input_buffer()
                    if self.send_command(0x03) is not None:
                        logger.info(f"  OK Radio responded at {baud} baud!")
                        self.baudrate = baud
                        result['detected_baud'] = baud
                        result['frequency_hz'] = self.read_frequency()
                        break
                except Exception as e:
                    logger.warning(f"  Baud {baud} error: {e}")
            if 'detected_baud' not in result:
                self.serial_conn.baudrate = self.baudrate
                result['error'] = (
                    'No response at any baud rate. Check: '
                    '(1) CI-V Address in radio menu matches app config, '
                    '(2) CI-V USB Baud Rate in radio menu matches app config, '
                    '(3) Radio powered on, '
                    '(4) USB cable seated properly.'
                )

        result['mode']      = self.read_mode()
        result['tx_state']  = self.read_tx_state()
        result['smeter_raw'] = self.read_smeter()
        result['responding'] = result['frequency_hz'] is not None
        logger.info(f"=== Probe: {'OK RESPONDING' if result['responding'] else 'FAIL NOT RESPONDING'} ===")
        return result

    @staticmethod
    def list_ports():
        return [p.device for p in serial.tools.list_ports.comports()]

    @staticmethod
    def score_ports():
        """Return all serial ports scored by likelihood of being an Icom radio."""
        results = []
        for p in serial.tools.list_ports.comports():
            # Skip native UARTs -- they are never an Icom radio and take ages to timeout
            import re as _re
            if p.device.startswith('/dev/ttyS') and p.device[9:].isdigit():
                continue
            hwid  = (p.hwid        or '').lower()
            desc  = (p.description or '').lower()
            manuf = (p.manufacturer or '').lower()
            score = 0
            reasons = []
            if '10c4' in hwid or 'cp210' in hwid or 'silabs' in desc:
                score += 3; reasons.append('SiLabs CP210x (Icom standard chip)')
            if 'icom' in desc or 'icom' in manuf:
                score += 5; reasons.append('Icom in description')
            if 'ic-7610' in desc.lower() or 'ic-7610' in hwid.lower():
                score += 10; reasons.append('IC-7610 identified')
            if '0403' in hwid or 'ftdi' in desc:
                score += 2; reasons.append('FTDI chip')
            if 'ttyusb' in p.device.lower():
                score += 1; reasons.append('USB serial')
            results.append({
                'device':      p.device,
                'description': p.description,
                'hwid':        p.hwid,
                'manufacturer': p.manufacturer,
                'vid':         f'0x{p.vid:04X}' if p.vid else None,
                'pid':         f'0x{p.pid:04X}' if p.pid else None,
                'score':       score,
                'reasons':     reasons,
            })
        results.sort(key=lambda x: x['score'], reverse=True)
        return results

# -------------------------------------------------------------
# TTS Agents
# -------------------------------------------------------------
class PiperTTSAgent:
    def synthesize(self, text, voice=None, output_path=None):
        voice      = voice or DEFAULT_PIPER_VOICE
        voice_info = PIPER_VOICES.get(voice, list(PIPER_VOICES.values())[0] if PIPER_VOICES else None)
        if not voice_info:
            logger.error('Piper: no voices configured -- install a Piper voice model')
            return None
        model = voice_info['model']
        if not os.path.exists(model):
            logger.error(
                f'Piper model not found: {model} -- '
                f'install Piper voices to {PIPER_VOICES_DIR} or switch engine to eSpeak'
            )
            # Return None so the caller surfaces an error rather than silently
            # falling back to eSpeak (which reads text phonetically).
            return None
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(_fd)
        try:
            result = subprocess.run(
                ['piper', '--model', model, '--output_file', output_path],
                input=text.encode('utf-8'), capture_output=True, timeout=30
            )
            if result.returncode != 0 or not os.path.exists(output_path) \
                    or os.path.getsize(output_path) == 0:
                raise RuntimeError(result.stderr.decode('utf-8', errors='replace').strip())
            return output_path
        except FileNotFoundError:
            logger.error(
                'Piper binary not found -- install piper-tts or switch engine to eSpeak'
            )
            return None
        except Exception as e:
            logger.error(f'Piper TTS error: {e}')
            return None


class EspeakTTSAgent:
    def synthesize(self, text, voice='en-us', output_path=None):
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(_fd)
        try:
            # Pass text via stdin (not as CLI arg) to avoid espeak phonetic
            # interpretation of certain argument patterns.  --punct suppresses
            # punctuation-as-speech; omitting '-m' ensures plain text mode.
            subprocess.run(
                ['espeak-ng', '-v', voice, '-s', '150', '-p', '50',
                 '--punct', '-w', output_path],
                input=text.encode('utf-8'),
                check=True, capture_output=True, timeout=20
            )
            return output_path
        except Exception as e:
            logger.error(f"eSpeak TTS error: {e}")
            return None


class SpeechifyTTSAgent:
    """Speechify API TTS -- https://docs.sws.speechify.com"""

    @staticmethod
    def _get_key():
        if _api_keys_ok:
            k = _api_keys.get_key('speechify', 'api_key')
            if k: return k
        return os.environ.get('SPEECHIFY_API_KEY', '')

    @staticmethod
    def _get_voice():
        if _api_keys_ok:
            v = _api_keys.get_key('speechify', 'default_voice')
            if v: return v
        return os.environ.get('SPEECHIFY_VOICE', 'henry')

    def synthesize(self, text, voice=None, output_path=None):
        api_key = self._get_key()
        if not api_key:
            return None
        voice = voice or self._get_voice() or 'henry'
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.mp3')
            os.close(_fd)
        try:
            resp = requests.post(
                'https://api.sws.speechify.com/v1/audio/speech',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type':  'application/json',
                    'Accept':        'audio/mpeg',
                },
                json={
                    'input':   f'<speak>{text}</speak>',
                    'voice_id': voice,
                    'audio_format': 'mp3',
                },
                timeout=30
            )
            if resp.status_code == 200:
                # Guard against Speechify returning HTTP 200 with a JSON error body
                # instead of audio (happens with invalid voice_id or plan limits).
                # MP3 files start with 0xFF 0xFB/0xF3/0xF2 (MPEG frame sync) or
                # 0x49 0x44 0x33 (ID3 tag). Anything else is not audio.
                content = resp.content
                ct = resp.headers.get('Content-Type', '')
                is_audio = (
                    'audio' in ct or
                    (len(content) >= 2 and content[0] == 0xFF and content[1] in (0xFB, 0xF3, 0xF2, 0xFA, 0xE3)) or
                    (len(content) >= 3 and content[:3] == b'ID3')
                )
                if not is_audio:
                    # Speechify returned a non-audio body - log it and fail cleanly
                    try:
                        err_text = content[:300].decode('utf-8', errors='replace')
                    except Exception:
                        err_text = repr(content[:80])
                    logger.error(f'Speechify TTS: HTTP 200 but response is not MP3 audio '
                                 f'(Content-Type: {ct!r}) -- voice_id={voice!r} -- body: {err_text}')
                    return None
                with open(output_path, 'wb') as fp:
                    fp.write(content)
                logger.info(f'Speechify TTS: {len(text)} chars -> {output_path} ({len(content)} bytes)')
                return output_path
            else:
                logger.error(f"Speechify TTS error: HTTP {resp.status_code} -- {resp.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"Speechify TTS exception: {e}")
            return None

    def get_voices(self):
        api_key = self._get_key()
        if not api_key:
            return {}
        try:
            r = requests.get(
                'https://api.sws.speechify.com/v1/voices',
                headers={'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'},
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                voices = data if isinstance(data, list) else data.get('voices', [])
                def _spfy_name(v, i):
                    # Speechify API uses various field names across versions
                    for field in ('displayName', 'display_name', 'name', 'title', 'label', 'voice_name'):
                        if v.get(field):
                            return str(v[field])
                    # Build a readable name from language + gender if available
                    lang   = v.get('language', v.get('lang', ''))
                    gender = v.get('gender', '')
                    vid    = v.get('id', v.get('voice_id', ''))
                    if lang or gender:
                        parts = [p for p in [lang, gender] if p]
                        return f"{' '.join(parts)} ({vid})" if vid else ' '.join(parts)
                    return vid or f"Voice {i+1}"
                return {v.get('id', v.get('voice_id', str(i))): _spfy_name(v, i)
                        for i, v in enumerate(voices)}
        except Exception as e:
            logger.warning(f"Speechify get_voices error: {e}")
        return {}


class ElevenLabsTTSAgent:
    def synthesize(self, text, voice_id=None, output_path=None):
        if not ELEVENLABS_API_KEY:
            return None
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.mp3')
            os.close(_fd)
        voice_id = voice_id or 'EXAVITQu4vr4xnSDxMaL'
        try:
            resp = requests.post(
                f'https://api.elevenlabs.io/v1/text-to-speech/{voice_id}',
                headers={'xi-api-key': ELEVENLABS_API_KEY, 'Content-Type': 'application/json'},
                json={'text': text, 'model_id': 'eleven_monolingual_v1',
                      'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75}},
                timeout=30
            )
            resp.raise_for_status()
            with open(output_path, 'wb') as f:
                f.write(resp.content)
            return output_path
        except Exception as e:
            logger.error(f"ElevenLabs TTS error: {e}")
            return None

    @staticmethod
    def get_voices():
        if not ELEVENLABS_API_KEY:
            return {}
        try:
            resp = requests.get('https://api.elevenlabs.io/v1/voices',
                                headers={'xi-api-key': ELEVENLABS_API_KEY}, timeout=10)
            return {v['voice_id']: v['name'] for v in resp.json().get('voices', [])}
        except Exception:
            return {}


# -------------------------------------------------------------
# FastKoko TTS Agent  (local Kokoro-FastAPI server)
# No API key - just a LAN URL stored in api_keys.json
# Endpoint: POST /v1/audio/speech  (OpenAI-compatible)
# Voices:   GET  /v1/audio/voices
# -------------------------------------------------------------
class FastKokoTTSAgent:

    @staticmethod
    def _get_url() -> str:
        if _api_keys_ok:
            u = _api_keys.get_key('fastkoko', 'url')
            if u:
                return u.strip().rstrip('/')
        return os.environ.get('FASTKOKO_URL', '').strip().rstrip('/')

    @staticmethod
    def _get_default_voice() -> str:
        if _api_keys_ok:
            v = _api_keys.get_key('fastkoko', 'default_voice')
            if v:
                return v.strip()
        return os.environ.get('FASTKOKO_VOICE', 'af_sarah')

    def synthesize(self, text: str, voice: str = None, output_path: str = None) -> str | None:
        url = self._get_url()
        if not url:
            logger.error('FastKoko TTS: no server URL configured')
            return None
        voice = (voice or self._get_default_voice() or 'af_sarah').strip()
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(_fd)
        try:
            resp = requests.post(
                f'{url}/v1/audio/speech',
                headers={'Content-Type': 'application/json', 'Accept': 'audio/wav'},
                json={'model': 'kokoro', 'input': text, 'voice': voice, 'response_format': 'wav'},
                timeout=60,
            )
            if resp.status_code != 200:
                logger.error(f'FastKoko TTS: HTTP {resp.status_code} -- {resp.text[:200]}')
                return None
            # Validate WAV: must start with RIFF header
            content = resp.content
            if len(content) < 4 or content[:4] != b'RIFF':
                try:
                    body = content[:200].decode('utf-8', errors='replace')
                except Exception:
                    body = repr(content[:80])
                logger.error(f'FastKoko TTS: response is not a WAV file -- body: {body}')
                return None
            with open(output_path, 'wb') as fp:
                fp.write(content)
            logger.info(f'FastKoko TTS: {len(text)} chars, voice={voice} -> {output_path} ({len(content)} bytes)')
            return output_path
        except requests.exceptions.ConnectionError:
            logger.error(f'FastKoko TTS: cannot connect to {url}')
            return None
        except Exception as e:
            logger.error(f'FastKoko TTS exception: {e}')
            return None

    def get_voices(self) -> list[str]:
        url = self._get_url()
        if not url:
            return []
        try:
            resp = requests.get(f'{url}/v1/audio/voices', timeout=8)
            if resp.status_code == 200:
                return resp.json().get('voices', [])
        except Exception as e:
            logger.warning(f'FastKoko get_voices error: {e}')
        return []


# -------------------------------------------------------------
# Audio Effects
# -------------------------------------------------------------
# -------------------------------------------------------------
# Edge TTS Agent  (Microsoft Neural voices, free, no key)
# pip install edge-tts
# -------------------------------------------------------------
class EdgeTTSAgent:
    # Good subset of the 400+ available voices
    VOICES = {
        'en-US-AriaNeural':       'Aria (US Female)',
        'en-US-GuyNeural':        'Guy (US Male)',
        'en-US-JennyNeural':      'Jenny (US Female)',
        'en-US-EricNeural':       'Eric (US Male)',
        'en-GB-SoniaNeural':      'Sonia (UK Female)',
        'en-GB-RyanNeural':       'Ryan (UK Male)',
        'en-AU-NatashaNeural':    'Natasha (AU Female)',
        'en-AU-WilliamNeural':    'William (AU Male)',
        'en-IE-EmilyNeural':      'Emily (IE Female)',
        'en-IN-NeerjaNeural':     'Neerja (IN Female)',
        'en-NG-AbeoNeural':       'Abeo (NG Male)',
        'en-ZA-LeahNeural':       'Leah (ZA Female)',
        'en-US-SteffanNeural':    'Steffan (US Male)',
        'en-US-AnaNeural':        'Ana (US Child)',
    }

    def synthesize(self, text, voice=None, output_path=None):
        try:
            import edge_tts, asyncio
        except ImportError:
            logger.error('edge-tts not installed: pip install edge-tts')
            return None
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.mp3')
            os.close(_fd)
        voice = voice or 'en-US-AriaNeural'
        try:
            async def _synth():
                comm = edge_tts.Communicate(text, voice)
                await comm.save(output_path)
            asyncio.run(_synth())
            return output_path
        except Exception as e:
            logger.error(f'EdgeTTS error: {e}')
            return None

    @staticmethod
    def get_voices():
        return EdgeTTSAgent.VOICES


# -------------------------------------------------------------
# gTTS Agent  (Google Text-to-Speech, free, no key required)
# pip install gtts
# -------------------------------------------------------------
class GTTSAgent:
    VOICES = {
        'en':    'English',
        'en-uk': 'English (UK)',
        'en-au': 'English (AU)',
        'en-ca': 'English (CA)',
        'en-in': 'English (IN)',
        'es':    'Spanish',
        'fr':    'French',
        'de':    'German',
        'it':    'Italian',
        'pt':    'Portuguese',
        'ja':    'Japanese',
        'ko':    'Korean',
        'zh':    'Chinese',
        'ar':    'Arabic',
        'ru':    'Russian',
        'hi':    'Hindi',
    }

    def synthesize(self, text, voice=None, output_path=None, slow=False):
        try:
            from gtts import gTTS
        except ImportError:
            logger.error('gtts not installed: pip install gtts')
            return None
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.mp3')
            os.close(_fd)
        lang = voice or 'en'
        tld  = 'co.uk' if lang == 'en-uk' else \
               'com.au' if lang == 'en-au' else \
               'ca'     if lang == 'en-ca' else \
               'co.in'  if lang == 'en-in' else 'com'
        lang_code = lang.split('-')[0]
        try:
            tts = gTTS(text=text, lang=lang_code, tld=tld, slow=slow)
            tts.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f'gTTS error: {e}')
            return None

    @staticmethod
    def get_voices():
        return GTTSAgent.VOICES


# -------------------------------------------------------------
# pyttsx3 Agent  (offline, system TTS -- espeak/SAPI/NSS)
# pip install pyttsx3
# -------------------------------------------------------------
class Pyttsx3Agent:
    VOICES = {
        'default': 'System Default',
        'en':      'English',
        'en_US':   'English (US)',
        'en_GB':   'English (GB)',
        'es':      'Spanish',
        'fr':      'French',
        'de':      'German',
    }

    def synthesize(self, text, voice=None, output_path=None, rate=150, volume=1.0):
        try:
            import pyttsx3
        except ImportError:
            logger.error('pyttsx3 not installed: pip install pyttsx3')
            return None
        if not output_path:
            _fd, output_path = tempfile.mkstemp(suffix='.wav')
            os.close(_fd)
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate',   rate)
            engine.setProperty('volume', volume)
            if voice and voice != 'default':
                voices = engine.getProperty('voices')
                for v in voices:
                    if voice.lower() in v.id.lower() or voice.lower() in (v.name or '').lower():
                        engine.setProperty('voice', v.id)
                        break
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            return output_path if os.path.exists(output_path) else None
        except Exception as e:
            logger.error(f'pyttsx3 error: {e}')
            return None

    @staticmethod
    def get_voices():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            engine.runAndWait()
            engine.stop()
            return {v.id: v.name or v.id for v in voices} if voices else Pyttsx3Agent.VOICES
        except Exception:
            return Pyttsx3Agent.VOICES



class AudioEffectsAgent:
    PRESETS = {
        # -- Core --------------------------------------------------
        'autotune':    {'pitch': 0,    'speed': 1.0, 'reverb': False, 'robot': False, 'autotune': True},
        'normal':      {'pitch': 0,    'speed': 1.0, 'reverb': False, 'robot': False},
        'radio':       {'pitch': 0,    'speed': 1.0, 'reverb': False, 'robot': False, 'radio': True},
        # -- Classic dub/voice effects -----------------------------
        'chipmunk':    {'pitch': 800,  'speed': 1.3, 'reverb': False, 'robot': False},
        'robot':       {'pitch': 0,    'speed': 1.0, 'reverb': False, 'robot': True},
        'darth_vader': {'pitch': -500, 'speed': 0.8, 'reverb': True,  'robot': False},
        'deep':        {'pitch': -300, 'speed': 0.9, 'reverb': False, 'robot': False},
        # -- New effects -------------------------------------------
        'submarine':   {'pitch': -700, 'speed': 0.75,'reverb': True,  'robot': False, 'lowpass': 800},
        'megaphone':   {'pitch': 100,  'speed': 1.0, 'reverb': False, 'robot': False, 'megaphone': True},
        'telephone':   {'pitch': 0,    'speed': 1.0, 'reverb': False, 'robot': False, 'telephone': True},
        'whisper':     {'pitch': 200,  'speed': 0.85,'reverb': False, 'robot': False, 'whisper': True},
        'stadium':     {'pitch': 0,    'speed': 1.0, 'reverb': True,  'robot': False, 'stadium': True},
        'echo':        {'pitch': 0,    'speed': 1.0, 'reverb': False, 'robot': False, 'echo': True},
        'ghost':       {'pitch': -200, 'speed': 0.9, 'reverb': True,  'robot': False, 'chorus': True},
        'cave':        {'pitch': -150, 'speed': 0.95,'reverb': True,  'robot': False, 'cave': True},
        'alien':       {'pitch': 400,  'speed': 1.1, 'reverb': False, 'robot': True,  'flanger': True},
        'walkie':      {'pitch': 50,   'speed': 1.0, 'reverb': False, 'robot': False, 'walkie': True},
        'horror':      {'pitch': -600, 'speed': 0.7, 'reverb': True,  'robot': False, 'tremolo': True},
        'newsroom':    {'pitch': 0,    'speed': 1.05,'reverb': False, 'robot': False, 'newsroom': True},
        'vintage':     {'pitch': -100, 'speed': 0.95,'reverb': False, 'robot': False, 'vintage': True},
    }

    def apply(self, input_path, preset='normal', pitch=0, speed=1.0, reverb=0,
             echo=0, chorus=0, flanger=0, tremolo=0, overdrive=0, bitcrush=0):
        if not input_path or not os.path.exists(input_path):
            return input_path
        cfg = self.PRESETS.get(preset, self.PRESETS['normal']).copy()
        if pitch != 0:       cfg['pitch']     = pitch
        if speed != 1.0:     cfg['speed']     = speed
        if reverb > 0:       cfg['reverb']    = reverb   # 0-100 intensity
        if echo > 0:         cfg['echo_fx']   = echo
        if chorus > 0:       cfg['chorus_fx'] = chorus
        if flanger > 0:      cfg['flange_fx'] = flanger
        if tremolo > 0:      cfg['trem_fx']   = tremolo
        if overdrive > 0:    cfg['drive_fx']  = overdrive
        if bitcrush > 0:     cfg['crush_fx']  = bitcrush

        _fd, output_path = tempfile.mkstemp(suffix='.wav')
        os.close(_fd)
        mp3_wav = None   # tracks intermediate mp3->wav conversion file
        try:
            if input_path.endswith('.mp3'):
                _fd, mp3_wav = tempfile.mkstemp(suffix='.wav')
                os.close(_fd)
                subprocess.run(['ffmpeg', '-y', '-i', input_path, mp3_wav],
                               capture_output=True, check=True)
                input_path = mp3_wav

            sox_cmd = ['sox', input_path, output_path]
            if cfg.get('robot'):
                sox_cmd += ['overdrive', '20', 'band', '1000', '500', 'overdrive', '20']
            if cfg.get('radio'):
                sox_cmd += ['highpass', '300', 'lowpass', '3000', 'overdrive', '5']
            if cfg.get('walkie'):
                sox_cmd += ['highpass', '500', 'lowpass', '2800', 'overdrive', '10', 'compand', '0.1,0.3', '6:-70,-60,-20', '-5', '-90', '0.2']
            if cfg.get('telephone'):
                sox_cmd += ['highpass', '400', 'lowpass', '3400', 'overdrive', '8', 'vol', '0.8']
            if cfg.get('megaphone'):
                sox_cmd += ['highpass', '700', 'lowpass', '4000', 'overdrive', '30', 'vol', '1.2']
            if cfg.get('whisper'):
                sox_cmd += ['vol', '0.3', 'overdrive', '5', 'highpass', '2000']
            if cfg.get('echo'):
                sox_cmd += ['echo', '0.8', '0.88', '60', '0.4']
            if cfg.get('cave'):
                sox_cmd += ['echo', '0.8', '0.88', '120', '0.3', '240', '0.2']
            if cfg.get('chorus'):
                sox_cmd += ['chorus', '0.7', '0.9', '55', '0.4', '0.25', '2', '-t']
            if cfg.get('flanger'):
                sox_cmd += ['flanger', '0', '2', '0', '71', '0.5', 'lin', '0', '25']
            if cfg.get('tremolo'):
                sox_cmd += ['tremolo', '5', '80']
            if cfg.get('stadium'):
                sox_cmd += ['reverb', '80', '80', '100', '100', '0', '0']
            if cfg.get('autotune'):
                # Simulate autotune: pitch quantize via heavy chorus+flanger modulation
                # combined with a slight robotic quality and pitch snap
                sox_cmd += ['chorus', '0.5', '0.9', '50', '0.4', '0.5', '2.0', '-s',
                            'flanger', '0', '3', '0', '71', '0.5', 'lin', '0', '25',
                            'pitch', '0', 'overdrive', '5']
            if cfg.get('vintage'):
                sox_cmd += ['highpass', '200', 'lowpass', '6000', 'vol', '0.9', 'overdrive', '3']
            if cfg.get('newsroom'):
                sox_cmd += ['highpass', '250', 'lowpass', '7500', 'overdrive', '2']
            if cfg.get('lowpass'):
                sox_cmd += ['lowpass', str(cfg['lowpass'])]
            if cfg.get('speed', 1.0) != 1.0:
                sox_cmd += ['tempo', str(cfg['speed'])]
            if cfg.get('pitch', 0) != 0:
                sox_cmd += ['pitch', str(cfg['pitch'])]
            # -- Progressive reverb (0-100 intensity) -----------
            rv = cfg.get('reverb', 0)
            if rv and rv is not True:
                rev_wet   = max(0, min(100, int(rv)))
                rev_room  = 20 + int(rv * 0.8)          # 20-100
                rev_damp  = max(20, 80 - int(rv * 0.5)) # 80-30
                sox_cmd += ['reverb', str(rev_wet), str(rev_damp), str(rev_room)]
            elif rv:  # preset True (backwards compat)
                sox_cmd += ['reverb', '50', '50', '100']

            # -- Bizarre FX from sliders -----------------------
            if cfg.get('echo_fx', 0) > 0:
                echo_delay  = 40 + int(cfg['echo_fx'] * 0.8)  # 40-120ms
                echo_decay  = round(0.2 + cfg['echo_fx'] / 100.0 * 0.65, 2)
                sox_cmd += ['echo', '0.8', str(echo_decay), str(echo_delay), str(echo_decay)]
            if cfg.get('chorus_fx', 0) > 0:
                c = cfg['chorus_fx'] / 100.0
                sox_cmd += ['chorus', str(round(0.5+c*0.3,2)), '0.9',
                            str(40+int(c*30)), str(round(0.3+c*0.2,2)),
                            str(round(0.2+c*0.3,2)), '2', '-t']
            if cfg.get('flange_fx', 0) > 0:
                sox_cmd += ['flanger', '0', str(int(1+cfg['flange_fx']/20)),
                            '0', '71', '0.5', 'lin', '0', '25']
            if cfg.get('trem_fx', 0) > 0:
                freq  = round(2.0 + cfg['trem_fx'] / 100.0 * 8.0, 1)
                depth = round(40 + cfg['trem_fx'] * 0.55)
                sox_cmd += ['tremolo', str(freq), str(depth)]
            if cfg.get('drive_fx', 0) > 0:
                gain = round(1 + cfg['drive_fx'] / 100.0 * 40, 1)
                sox_cmd += ['overdrive', str(int(cfg['drive_fx'])), '0', 'vol', str(round(1/max(1,gain*0.5),2))]
            if cfg.get('crush_fx', 0) > 0:
                bits = max(1, 13 - int(cfg['crush_fx']))
                sox_cmd += ['rate', '8000', 'rate', '44100']  # lo-fi rate crush

            if len(sox_cmd) == 3:
                import shutil
                shutil.copy(input_path, output_path)
            else:
                subprocess.run(sox_cmd, capture_output=True, check=True)
            return output_path
        except Exception as e:
            logger.warning(f"Audio effects error: {e}")
            # Clean up the unused output file and return original
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except Exception:
                pass
            return input_path
        finally:
            # Clean up the mp3->wav intermediate file if it was created
            if mp3_wav and os.path.exists(mp3_wav):
                try:
                    os.remove(mp3_wav)
                except Exception:
                    pass


# -------------------------------------------------------------
# Audio Playback
# -------------------------------------------------------------
class AudioPlaybackAgent:
    def play(self, file_path, device=None, normalize=True):
        device = device or AUDIO_DEVICE
        if not file_path or not os.path.exists(file_path):
            logger.error(f"Audio file not found: {file_path}")
            return False

        play_file = file_path
        processed = None  # track ffmpeg-normalized temp file for cleanup

        gain_db = float(os.environ.get('AUDIO_GAIN_DB', '0'))
        if normalize or gain_db != 0.0:
            try:
                _fd, processed = tempfile.mkstemp(suffix='.wav')
                os.close(_fd)
                filters = []
                if normalize:
                    filters.append('loudnorm=I=-20:TP=-2:LRA=11')
                if gain_db != 0.0:
                    filters.append(f'volume={gain_db}dB')
                r = subprocess.run(
                    ['ffmpeg', '-y', '-i', file_path,
                     '-af', ','.join(filters) if filters else 'anull', processed],
                    capture_output=True, timeout=15
                )
                if r.returncode == 0:
                    play_file = processed
                else:
                    logger.warning(f"ffmpeg audio processing failed (rc={r.returncode})")
            except Exception as e:
                logger.warning(f"ffmpeg audio processing error: {e}")

        # Try devices in order: configured -> default -> bare aplay
        devices_to_try = [device]
        if device != 'default':
            devices_to_try.append('default')
        devices_to_try.append(None)

        global _active_tx_proc
        for dev in devices_to_try:
            try:
                cmd = ['aplay']
                if dev:
                    cmd += ['-D', dev]
                cmd.append(play_file)
                logger.info(f"aplay: device={dev or 'system-default'} file={play_file}")
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.PIPE)
                _active_tx_proc = proc
                try:
                    _, stderr_bytes = proc.communicate(timeout=300)
                finally:
                    _active_tx_proc = None
                if proc.returncode == 0:
                    logger.info(f"aplay: complete (device={dev or 'system-default'})")
                    if processed and processed != file_path and os.path.exists(processed):
                        try: os.remove(processed)
                        except Exception: pass
                    return True
                if proc.returncode == -15 or proc.returncode == -9:
                    # Killed by terminate endpoint
                    logger.info("aplay: terminated by user")
                    if processed and processed != file_path and os.path.exists(processed):
                        try: os.remove(processed)
                        except Exception: pass
                    return False
                err = (stderr_bytes or b'').decode().strip()
                logger.warning(f"aplay failed device={dev}: rc={proc.returncode} {err}")
            except subprocess.TimeoutExpired:
                if _active_tx_proc:
                    _active_tx_proc.kill()
                    _active_tx_proc = None
                logger.error("aplay timed out")
                return False
            except Exception as e:
                _active_tx_proc = None
                logger.warning(f"aplay error device={dev}: {e}")

        logger.error("aplay: all devices failed")
        # Clean up normalized temp file if it was created
        if processed and processed != file_path and os.path.exists(processed):
            try:
                os.remove(processed)
            except Exception:
                pass
        return False


# -------------------------------------------------------------
# Roger Beep
# -------------------------------------------------------------
def play_roger_beep():
    if os.path.exists(ROGER_BEEP_FILE):
        try:
            cmd = ['aplay']
            if AUDIO_DEVICE:
                cmd += ['-D', AUDIO_DEVICE]
            cmd.append(ROGER_BEEP_FILE)
            subprocess.run(cmd, capture_output=True, timeout=10)
        except Exception as e:
            logger.warning(f"Roger beep error: {e}")


# -------------------------------------------------------------
# SSTV
# -------------------------------------------------------------
def _build_sstv_modes_map():
    """Return {name: class} for all pysstv color+bw modes."""
    try:
        from pysstv import color as _c
        cmap = {n: c for n, c in inspect.getmembers(_c, inspect.isclass)
                if hasattr(c, 'WIDTH') and not n.startswith('_')}
    except Exception:
        cmap = {}
    try:
        from pysstv import grayscale as _g
        gmap = {n: c for n, c in inspect.getmembers(_g, inspect.isclass)
                if hasattr(c, 'WIDTH') and not n.startswith('_')}
    except Exception:
        gmap = {}
    merged = {}
    merged.update(gmap)
    merged.update(cmap)   # color takes precedence on name collision
    return merged

# Full static metadata table used by both backend and frontend.
# [width, height, tx_seconds, color_type, family, description]
SSTV_MODE_META = {
    'Robot8BW':     [160, 120,   8,  'BW',    'Robot',   'Fastest mode, emergency use, B&W'],
    'Robot24BW':    [160, 120,  24,  'BW',    'Robot',   'Fast mono, good for quick check-ins'],
    'Robot36':      [320, 240,  36,  'Color', 'Robot',   'Most popular short mode, YC encoding'],
    'Robot72':      [320, 240,  72,  'Color', 'Robot',   'Higher quality Robot, 2x Robot36 time'],
    'MartinM1':     [320, 256, 114,  'Color', 'Martin',  'HF workhorse, dominant mode in Europe'],
    'MartinM2':     [320, 256,  58,  'Color', 'Martin',  'Half-speed Martin, good quality/time tradeoff'],
    'ScottieS1':    [320, 256, 110,  'Color', 'Scottie', 'Dominant in North America, RGB encoding'],
    'ScottieS2':    [320, 256,  71,  'Color', 'Scottie', 'Faster Scottie, slightly lower quality'],
    'ScottieDX':    [320, 256, 269,  'Color', 'Scottie', 'Highest quality Scottie, 4.5 min'],
    'PD90':         [320, 240,  90,  'Color', 'PD',      'Fast PD, YC encoding, good 320x240'],
    'PD120':        [640, 496, 126,  'Color', 'PD',      'HD quality, 2:1 aspect, popular HF'],
    'PD160':        [512, 400, 161,  'Color', 'PD',      'Medium-high res, intermediate time'],
    'PD180':        [640, 496, 187,  'Color', 'PD',      'Best practical HF quality, 3 min'],
    'PD240':        [640, 496, 248,  'Color', 'PD',      'Near-photo quality, 4 min'],
    'PD290':        [800, 616, 290,  'Color', 'PD',      'Maximum PD resolution, 4.8 min'],
    'PasokonP3':    [640, 496, 203,  'Color', 'Pasokon', 'High-res Japanese mode, RGB, 3.4 min'],
    'PasokonP5':    [640, 496, 305,  'Color', 'Pasokon', 'Ultra-high res Pasokon, 5 min'],
    'PasokonP7':    [640, 496, 406,  'Color', 'Pasokon', 'Maximum Pasokon quality, 6.8 min'],
    'WraaseSC2120': [320, 256, 120,  'Color', 'Wraase',  'Wraase SC-2 120, 2min, RGB'],
    'WraaseSC2180': [320, 256, 182,  'Color', 'Wraase',  'Wraase SC-2 180, 3min, high quality RGB'],
}


def image_to_sstv(image_path, output_wav, mode='Robot36',
                  vox=False, fskid='', keep_aspect=False):
    """Encode image to SSTV WAV. Returns True on success."""
    try:
        from PIL import Image, ImageOps
        modes_map = _build_sstv_modes_map()
        sstv_class = modes_map.get(mode)
        if not sstv_class:
            logger.error(f"SSTV mode '{mode}' not found. Available: {sorted(modes_map)}")
            return False
        w = getattr(sstv_class, 'WIDTH',  320)
        h = getattr(sstv_class, 'HEIGHT', 240)
        img = Image.open(image_path).convert('RGB')
        if keep_aspect:
            img.thumbnail((w, h), Image.LANCZOS)
            bg = Image.new('RGB', (w, h), (0, 0, 0))
            off_x = (w - img.width)  // 2
            off_y = (h - img.height) // 2
            bg.paste(img, (off_x, off_y))
            img = bg
        else:
            img = img.resize((w, h), Image.LANCZOS)
        sstv = sstv_class(img, 44100, 16)
        if vox:
            # pysstv: set vox_enabled attribute (different builds use different names)
            for _vox_attr in ('vox_enabled', 'add_vox_tones', 'vox'):
                try:
                    setattr(sstv, _vox_attr, True)
                    break
                except Exception:
                    pass
        if fskid and fskid.strip():
            try:
                sstv.fskid = fskid.strip().upper()
            except Exception:
                pass
        sstv.write_wav(output_wav)
        return True
    except Exception as e:
        logger.error(f"SSTV encode error: {e}")
        return False


# -------------------------------------------------------------
# Workflow Orchestrator
# -------------------------------------------------------------
class WorkflowOrchestrator:
    def __init__(self):
        self.icom_agent     = IcomSerialAgent()
        self.piper_agent    = PiperTTSAgent()
        self.espeak_agent   = EspeakTTSAgent()
        self.eleven_agent   = ElevenLabsTTSAgent()
        self.speechify_agent = SpeechifyTTSAgent()
        self.fastkoko_agent = FastKokoTTSAgent()
        self.effects_agent  = AudioEffectsAgent()
        self.playback_agent = AudioPlaybackAgent()
        self.edge_agent     = EdgeTTSAgent()
        self.gtts_agent     = GTTSAgent()
        self.pyttsx3_agent  = Pyttsx3Agent()
        self._connected     = False

    def connect(self, port=None, baud=None):
        self._connected = self.icom_agent.connect(port, baud)
        return self._connected

    def disconnect(self):
        self.icom_agent.disconnect()
        self._connected = False

    def execute(self, text, engine='piper', voice=None, preset='normal',
                pitch=0, speed=1.0, reverb=0, echo=0, chorus=0,
                flanger=0, tremolo=0, overdrive=0, bitcrush=0,
                roger_beep=True):
        global _poller_paused
        start      = time_module.time()
        audio_file = None   # raw TTS output
        fx_file    = None   # post-effects output (may differ from audio_file)
        ptt_active = False
        logger.info(
            f"execute: engine={engine} voice={voice} preset={preset} "
            f"pitch={pitch} speed={speed} reverb={reverb} roger_beep={roger_beep} "
            f"echo={echo} chorus={chorus} flanger={flanger} tremolo={tremolo} "
            f"overdrive={overdrive} bitcrush={bitcrush} "
            f"text={text[:60]!r}{'...' if len(text)>60 else ''}"
        )
        try:
            # -- TTS synthesis ------------------------------------------
            logger.debug(f"execute: synthesizing with engine={engine}")
            if engine == 'elevenlabs':
                audio_file = self.eleven_agent.synthesize(text, voice_id=voice)
            elif engine == 'speechify':
                audio_file = self.speechify_agent.synthesize(text, voice=voice)
            elif engine == 'fastkoko':
                audio_file = self.fastkoko_agent.synthesize(text, voice=voice)
            elif engine == 'edge':
                audio_file = self.edge_agent.synthesize(text, voice=voice)
            elif engine == 'gtts':
                audio_file = self.gtts_agent.synthesize(text, voice=voice)
            elif engine == 'pyttsx3':
                audio_file = self.pyttsx3_agent.synthesize(text, voice=voice)
            elif engine == 'espeak':
                audio_file = self.espeak_agent.synthesize(text)
            else:
                audio_file = self.piper_agent.synthesize(text, voice=voice)

            if not audio_file:
                logger.error(f"execute: synthesis returned None for engine={engine}")
                return {'success': False, 'message': 'TTS synthesis failed'}
            logger.debug(f"execute: synthesis OK -> {audio_file}")

            # -- Audio effects ------------------------------------------
            logger.debug(f"execute: applying effects preset={preset}")
            fx_file = self.effects_agent.apply(
                audio_file, preset=preset, pitch=pitch, speed=speed, reverb=reverb,
                echo=echo, chorus=chorus, flanger=flanger, tremolo=tremolo,
                overdrive=overdrive, bitcrush=bitcrush
            )
            logger.debug(f"execute: effects OK -> {fx_file}")

            # -- PTT ON -------------------------------------------------
            if self._connected:
                logger.info(
                    f"execute: PTT ON (port={self.icom_agent.port} "
                    f"ci_v=0x{self.icom_agent.ci_v_address:02X} "
                    f"baud={self.icom_agent.baudrate})"
                )
                _poller_paused = True   # stop poller from competing for the serial port
                time_module.sleep(0.1)  # let any in-flight poller command finish
                self.icom_agent.ptt_on()
                ptt_active = True
                time_module.sleep(0.3)  # radio settle before audio
            else:
                logger.warning("execute: radio not connected -- transmitting audio without PTT")

            # -- Audio playback -----------------------------------------
            logger.debug(f"execute: playing {fx_file}")
            self.playback_agent.play(fx_file)
            logger.debug("execute: playback complete")

            if roger_beep:
                play_roger_beep()

            # -- PTT OFF ------------------------------------------------
            if self._connected and ptt_active:
                time_module.sleep(0.2)
                self.icom_agent.ptt_off()
                ptt_active = False

            duration = round(time_module.time() - start, 2)
            logger.info(f"execute: complete in {duration}s")
            log_transmission(text, engine, voice, preset, duration, True, wav_path=fx_file)
            return {'success': True, 'message': 'Transmission complete', 'duration': duration}

        except Exception as e:
            logger.error(f"execute: workflow error: {e}", exc_info=True)
            log_transmission(text, engine, voice or '', preset, 0, False, str(e))
            return {'success': False, 'message': str(e)}
        finally:
            # Always ensure PTT is released and poller is unpaused
            if ptt_active:
                try:
                    self.icom_agent.ptt_off()
                except Exception:
                    pass
            _poller_paused = False
            # Clean up temp audio files (raw TTS and post-effects, which may be the same)
            for path in {audio_file, fx_file}:
                if path and os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass


# -------------------------------------------------------------
# Scheduler
# -------------------------------------------------------------
try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    scheduler = BackgroundScheduler()
    scheduler.start()
    logger.info("APScheduler started")
except ImportError:
    logger.warning("APScheduler not installed -- scheduling disabled")
    scheduler = None

# -------------------------------------------------------------
# Global Orchestrator
# -------------------------------------------------------------
orchestrator = WorkflowOrchestrator()

# -------------------------------------------------------------
# Live Dashboard -- SSE Radio State Poller
# -------------------------------------------------------------
_radio_state_lock = threading.Lock()
_radio_state = {
    'frequency': None, 'mode': None, 'smeter': None,
    'band': '', 'tx': False, 'last_update': None, 'error': None,
}
_sse_subscribers = []
_sse_lock        = threading.Lock()
_trenchtown_lock = threading.Lock()  # one PTT TX at a time in Trenchtown
_radio_poller_ctrl_tick = 0   # counts poller cycles for slow-poll of controls
_poller_paused   = False       # set True during PTT/TX to avoid serial bus contention


def _smeter_label(raw):
    """Convert IC-7610 BCD-decoded S-meter value to label.
    IC-7610 scale (decimal after BCD decode): 0=S0, 6=S1..60=S9, 70=S9+10dB .. 120=S9+60dB.
    """
    if raw is None: return '-'
    if raw <= 60:
        s = round(raw * 9 / 60)
        return f'S{min(s, 9)}'
    db = round((raw - 60) * 60 / 60)   # 60..120 maps to 0..60 dB over S9
    return f'S9+{min(db, 60)}dB'


def _freq_to_band(hz):
    if not hz: return ''
    mhz = hz / 1e6
    for lo, hi, name in [
        (1.8,2.0,'160m'),(3.5,4.0,'80m'),(7.0,7.3,'40m'),(10.1,10.15,'30m'),
        (14.0,14.35,'20m'),(18.068,18.168,'17m'),(21.0,21.45,'15m'),
        (24.89,24.99,'12m'),(28.0,29.7,'10m'),(50.0,54.0,'6m'),
        (144.0,148.0,'2m'),(420.0,450.0,'70cm'),
    ]:
        if lo <= mhz <= hi: return name
    return ''


def _radio_poller():
    global _radio_poller_ctrl_tick, _poller_paused
    _err_count = 0
    while True:
        # --- Pause during active TX to avoid serial bus contention ---
        if _poller_paused:
            time_module.sleep(0.2)
            continue

        state = {'frequency': None, 'mode': None, 'smeter': None,
                 'band': '', 'tx': False, 'last_update': _now_utc(), 'error': None,
                 'meters': {}, 'controls': {}}
        try:
            agent = orchestrator.icom_agent
            if agent.serial_conn and agent.serial_conn.is_open:
                # --- Read frequency first; if None, radio not responding --
                # Don't hammer 10 more slow-timeout reads if CI-V is dead.
                freq = agent.read_frequency()
                state['frequency'] = freq
                state['band']      = _freq_to_band(freq)

                if freq is None:
                    # Radio connected (serial open) but not answering CI-V.
                    # Log occasionally so the operator knows CI-V address/baud may be wrong.
                    if _err_count % 10 == 0:
                        logger.warning(
                            f"Radio poller: no CI-V response "
                            f"(port={agent.port} ci_v=0x{agent.ci_v_address:02X} "
                            f"baud={agent.baudrate}) -- check Settings"
                        )
                    _err_count += 1
                    state['error'] = 'CI-V no response'
                    with _radio_state_lock:
                        _radio_state.update(state)
                    time_module.sleep(2)   # back off before next poll
                    continue

                # CI-V is alive -- read the rest
                state['mode'] = agent.read_mode()
                raw           = agent.read_smeter()
                state['smeter'] = {
                    'raw':     raw,
                    'label':   _smeter_label(raw),
                    'percent': min(100, round((raw or 0) / 120 * 100)),
                }
                logger.debug(
                    f"Poller: freq={state['frequency']} mode={state['mode']} "
                    f"smeter={state['smeter']['label']} (raw={raw})"
                )
                state['tx']  = agent.read_tx_state()
                state['vfo'] = agent.read_vfo()

                # TX meters (only meaningful when transmitting, but read always)
                po   = agent.read_meter(0x11)
                swr  = agent.read_meter(0x12)
                alc  = agent.read_meter(0x13)
                comp = agent.read_meter(0x14)
                vd   = agent.read_meter(0x15)
                state['meters'] = {
                    'po':   {'raw': po,   'pct': min(100, round((po   or 0)/255*100))},
                    'swr':  {'raw': swr,  'pct': min(100, round((swr  or 0)/255*100))},
                    'alc':  {'raw': alc,  'pct': min(100, round((alc  or 0)/255*100))},
                    'comp': {'raw': comp, 'pct': min(100, round((comp or 0)/255*100))},
                    'vd':   {'raw': vd,   'pct': min(100, round((vd   or 0)/255*100))},
                }

                # Controls snapshot (polled slowly -- every 5th cycle)
                _radio_poller_ctrl_tick += 1
                if _radio_poller_ctrl_tick % 5 == 0:
                    state['controls'] = {
                        'af_gain':  agent.read_level(0x01),
                        'rf_gain':  agent.read_level(0x02),
                        'sql':      agent.read_level(0x03),
                        'rf_power': agent.read_level(0x0A),
                        'nr':       agent.read_function(0x40),
                        'nb':       agent.read_function(0x22),
                        'att':      agent.read_att(),
                        'preamp':   agent.read_preamp(),
                        'agc':      agent.read_agc(),
                        'split':    agent.read_split(),
                    }
                else:
                    with _radio_state_lock:
                        state['controls'] = _radio_state.get('controls', {})
                _err_count = 0  # reset backoff on successful poll
            else:
                state['error'] = 'Radio not connected'
        except Exception as e:
            state['error'] = str(e)
            _err_count += 1
            # Backoff: 1s, 2s, 4s, 8s, max 30s to avoid hammering on disconnect
            backoff = min(30, 2 ** min(_err_count - 1, 4))
            logger.debug(f"Radio poller exception (backoff {backoff}s): {e}")
            with _radio_state_lock:
                _radio_state.update(state)
            time_module.sleep(backoff)
            continue

        with _radio_state_lock:
            _radio_state.update(state)

        payload = json.dumps(_radio_state)
        with _sse_lock:
            dead = []
            for q in _sse_subscribers:
                try:    q.put_nowait(payload)
                except Exception: dead.append(q)
            for q in dead:
                _sse_subscribers.remove(q)

        time_module.sleep(1)



# -------------------------------------------------------------
# Beacon Mode
# -------------------------------------------------------------
_beacons      = {}
_beacon_lock  = threading.Lock()
_beacon_count = 0

_NATO = {
    'A':'Alpha','B':'Bravo','C':'Charlie','D':'Delta','E':'Echo','F':'Foxtrot',
    'G':'Golf','H':'Hotel','I':'India','J':'Juliet','K':'Kilo','L':'Lima',
    'M':'Mike','N':'November','O':'Oscar','P':'Papa','Q':'Quebec','R':'Romeo',
    'S':'Sierra','T':'Tango','U':'Uniform','V':'Victor','W':'Whiskey',
    'X':'X-ray','Y':'Yankee','Z':'Zulu',
    '0':'Zero','1':'One','2':'Two','3':'Three','4':'Four',
    '5':'Five','6':'Six','7':'Seven','8':'Eight','9':'Nine',
}

def _phonetic(callsign):
    return ' '.join(_NATO.get(c.upper(), c) for c in callsign if c.strip())

# ── CW / Morse synthesis ─────────────────────────────────────
_MORSE_TABLE = {
    'A':'.-',   'B':'-...', 'C':'-.-.', 'D':'-..',  'E':'.',    'F':'..-.',
    'G':'--.',  'H':'....', 'I':'..',   'J':'.---', 'K':'-.-',  'L':'.-..',
    'M':'--',   'N':'-.',   'O':'---',  'P':'.--.', 'Q':'--.-', 'R':'.-.',
    'S':'...',  'T':'-',    'U':'..-',  'V':'...-', 'W':'.--',  'X':'-..-',
    'Y':'-.--', 'Z':'--..',
    '0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....',
    '6':'-....','7':'--...','8':'---..',  '9':'----.',
    '.':'.-.-.-', ',':'--..--', '?':'..--..', '/':'-..-.', 'AR':'.-.-.',
    'SK':'...-.-', 'BT':'-...-', '+':'.-.-.',
}

def _cw_synthesize(text: str, wpm: int = 20, tone_hz: int = 700,
                   sample_rate: int = 8000) -> bytes:
    """Synthesize Morse CW as a raw 16-bit PCM WAV (returned as bytes)."""
    import numpy as np, struct
    unit = 1.2 / max(5, wpm)          # dit duration in seconds
    dit  = int(unit * sample_rate)
    dah  = dit * 3
    iel  = dit                        # inter-element gap (between dots/dashes)
    ich  = dit * 3                    # inter-character gap
    iw   = dit * 7                    # inter-word gap

    def tone(n_samples):
        t = np.linspace(0, n_samples / sample_rate, n_samples, endpoint=False)
        wave = (np.sin(2 * np.pi * tone_hz * t) * 32000 * 0.9).astype(np.int16)
        return wave

    silence = lambda n: np.zeros(n, dtype=np.int16)

    samples = []
    for word in text.upper().split():
        for ci, char in enumerate(word):
            code = _MORSE_TABLE.get(char)
            if code is None:
                continue
            for ei, element in enumerate(code):
                samples.append(tone(dah if element == '-' else dit))
                if ei < len(code) - 1:
                    samples.append(silence(iel))
            if ci < len(word) - 1:
                samples.append(silence(ich))
        samples.append(silence(iw))

    if not samples:
        pcm = silence(sample_rate)  # 1s silence if nothing encoded
    else:
        pcm = np.concatenate(samples)

    # Build WAV header
    n_samples  = len(pcm)
    data_bytes = pcm.tobytes()
    fmt_chunk  = struct.pack('<4sIHHIIHH', b'fmt ', 16, 1, 1,
                             sample_rate, sample_rate * 2, 2, 16)
    data_chunk = b'data' + struct.pack('<I', len(data_bytes)) + data_bytes
    riff       = b'RIFF' + struct.pack('<I', 4 + len(fmt_chunk) + len(data_chunk)) + b'WAVE'
    return riff + fmt_chunk + data_chunk


def _run_beacon_clip(bid, cfg):
    """Transmit a beacon by playing a Clips sound file over PTT."""
    sound_file = cfg.get('sound_file', '')
    if not sound_file:
        logger.error(f'Beacon {bid}: no sound_file configured')
        return
    clips_dir  = _clips_cfg().get('dir', CLIPS_DEFAULT_DIR)
    local_path = os.path.join(clips_dir, sound_file)
    s3_cache   = '/tmp/riggpt_clips_cache'
    cache_path = os.path.join(s3_cache, sound_file)
    path = local_path if os.path.exists(local_path) else \
           (cache_path if os.path.exists(cache_path) else None)
    if not path:
        logger.error(f'Beacon {bid}: clip not found: {sound_file}')
        return
    try:
        ptt_agent = orchestrator.icom_agent
        if orchestrator._connected:
            ptt_agent.ptt_on()
        dev = AUDIO_DEVICE or 'default'
        import subprocess
        subprocess.run(['aplay', '-D', dev, path], timeout=300, capture_output=True)
        if orchestrator._connected:
            ptt_agent.ptt_off()
        logger.info(f'Beacon {bid}: clip played: {sound_file}')
    except Exception as e:
        logger.error(f'Beacon {bid} clip error: {e}')
        try: orchestrator.icom_agent.ptt_off()
        except Exception: pass


def _run_beacon_cw(bid, cfg):
    """Transmit a CW beacon: synthesize tones and key PTT."""
    text = cfg.get('text', '')
    wpm  = int(cfg.get('cw_wpm', 20))
    # Optionally append callsign
    callsign = cfg.get('callsign', '').strip().upper()
    if callsign:
        text = f'{text} DE {callsign} AR'
    try:
        wav_bytes = _cw_synthesize(text, wpm=wpm)
        _fd, wav_path = tempfile.mkstemp(suffix='_cw.wav')
        os.close(_fd)
        with open(wav_path, 'wb') as f:
            f.write(wav_bytes)
        ptt_agent = orchestrator.icom_agent
        if orchestrator._connected:
            ptt_agent.ptt_on()
        import subprocess
        dev = AUDIO_DEVICE or 'default'
        subprocess.run(['aplay', '-D', dev, wav_path],
                       timeout=300, capture_output=True)
        if orchestrator._connected:
            ptt_agent.ptt_off()
    except Exception as e:
        logger.error(f'CW beacon {bid} error: {e}')
        try: orchestrator.icom_agent.ptt_off()
        except Exception: pass
    finally:
        try: os.unlink(wav_path)
        except Exception: pass


def _run_beacon(bid):
    with _beacon_lock:
        if bid not in _beacons: return
        cfg = dict(_beacons[bid]['config'])
    callsign = cfg.get('callsign', '')
    text     = cfg['text']
    if cfg.get('engine') == 'cw':
        _run_beacon_cw(bid, cfg)
    elif cfg.get('engine') == 'clip' or cfg.get('sound_file'):
        _run_beacon_clip(bid, cfg)
    else:
        if cfg.get('phonetic') and callsign:
            full = f"{text} This is {_phonetic(callsign)}"
        elif callsign:
            full = f"{text} This is {callsign}"
        else:
            full = text
        try:
            orchestrator.execute(
                full, engine=cfg.get('engine','piper'), voice=cfg.get('voice'),
                preset=cfg.get('preset','normal'), roger_beep=cfg.get('roger_beep',True),
            )
        except Exception as e:
            logger.error(f"Beacon {bid} error: {e}")
    with _beacon_lock:
        if bid in _beacons:
            _beacons[bid]['last_tx']  = _now_utc()
            _beacons[bid]['tx_count'] = _beacons[bid].get('tx_count', 0) + 1



# -------------------------------------------------------------
# Flask Routes -- Core
# -------------------------------------------------------------
@app.route('/')
def index():
    resp = make_response(render_template('index.html'))
    resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    resp.headers['Pragma']        = 'no-cache'
    resp.headers['Expires']       = '0'
    return resp


@app.route('/api/status')
def api_status():
    conn = orchestrator.icom_agent.serial_conn
    return jsonify({
        'version':               VERSION,
        'radio_model':           RADIO_MODEL,
        'serial_port':           orchestrator.icom_agent.port,
        'baud_rate':             orchestrator.icom_agent.baudrate,
        'ci_v_address':          f'0x{orchestrator.icom_agent.ci_v_address:02X}',
        'connected':             orchestrator._connected,
        'serial_open':           bool(conn and conn.is_open),
        'audio_device':          AUDIO_DEVICE,
        'elevenlabs_configured': bool(ELEVENLABS_API_KEY),
        'speechify_configured':  bool(SpeechifyTTSAgent._get_key()),
        'fastkoko_configured':   bool(FastKokoTTSAgent._get_url()),
        'scheduler_running':     bool(scheduler and scheduler.running),
    })


@app.route('/api/connect', methods=['POST'])
def api_connect():
    data   = request.json or {}
    port   = data.get('port') or SERIAL_PORT
    baud   = int(data.get('baud', BAUD_RATE))
    # CI-V address may arrive as a hex string ('0x80', '0x98') or plain int.
    # int(x, 0) auto-detects base: '0x80'->128, '128'->128, 128->TypeError.
    # Wrap in str() first so an already-integer default survives the call.
    ci_v_raw = data.get('ci_v_address', CI_V_ADDRESS)
    try:
        ci_v = int(str(ci_v_raw), 0)
    except (ValueError, TypeError):
        return jsonify({'success': False,
                        'message': f'Invalid CI-V address: {ci_v_raw!r} -- use decimal (128) or hex (0x80)'}), 400
    logger.info(f"api_connect: port={port} baud={baud} ci_v=0x{ci_v:02X} (from {ci_v_raw!r})")
    orchestrator.icom_agent.ci_v_address = ci_v
    success = orchestrator.connect(port, baud)
    return jsonify({'success': success,
                    'message': f'Connected to {port}' if success else 'Connection failed'})


@app.route('/api/disconnect', methods=['POST'])
def api_disconnect():
    orchestrator.disconnect()
    return jsonify({'success': True})


@app.route('/api/ports')
def api_ports():
    return jsonify({'ports': IcomSerialAgent.list_ports(),
                    'scored': IcomSerialAgent.score_ports()})


@app.route('/api/transmit', methods=['POST'])
def api_transmit():
    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'message': 'No text provided'}), 400

    delay  = max(0.0, min(30.0, float(data.get('delay_before_tx', 0) or 0)))
    repeat = max(1,   min(10,   int(data.get('repeat', 1) or 1)))

    if delay > 0:
        logger.info(f'TX delay: waiting {delay}s before transmit')
        time_module.sleep(delay)

    results = []
    for i in range(repeat):
        if i > 0:
            time_module.sleep(1.5)   # brief gap between repeats
        result = orchestrator.execute(
            text,
            engine     = data.get('engine', 'piper'),
            voice      = data.get('voice'),
            preset     = data.get('preset', 'normal'),
            pitch      = int(data.get('pitch', 0)),
            speed      = float(data.get('speed', 1.0)),
            reverb     = int(data.get('reverb', 0)),
            echo       = int(data.get('echo', 0)),
            chorus     = int(data.get('chorus', 0)),
            flanger    = int(data.get('flanger', 0)),
            tremolo    = int(data.get('tremolo', 0)),
            overdrive  = int(data.get('overdrive', 0)),
            bitcrush   = int(data.get('bitcrush', 0)),
            roger_beep = bool(data.get('roger_beep', True)),
        )
        results.append(result)
        if not result.get('success'):
            break   # abort remaining repeats on failure

    final = results[-1] if results else {'success': False, 'message': 'No result'}
    if repeat > 1:
        ok_count = sum(1 for r in results if r.get('success'))
        final['message'] = f'Transmitted {ok_count}/{repeat} times'
    return jsonify(final)


@app.route('/api/ptt', methods=['POST'])
def api_ptt():
    state = bool((request.json or {}).get('state', False))
    agent = orchestrator.icom_agent
    if not agent.serial_conn or not agent.serial_conn.is_open:
        return jsonify({'success': False, 'ptt': state,
                        'message': 'Radio not connected'}), 400
    if state: agent.ptt_on()
    else:     agent.ptt_off()
    return jsonify({'success': True, 'ptt': state})


@app.route('/api/voices/piper')
def api_piper_voices():
    return jsonify({
        'voices': {k: {'name': v['name'], 'available': os.path.exists(v['model'])}
                   for k, v in PIPER_VOICES.items()},
        'default': DEFAULT_PIPER_VOICE,
    })


@app.route('/api/voices/elevenlabs')
def api_elevenlabs_voices():
    if not ELEVENLABS_API_KEY:
        return jsonify({'error': 'ElevenLabs API key not configured', 'voices': {}})
    return jsonify({'voices': ElevenLabsTTSAgent.get_voices()})


# (old api_log removed -- extended version at bottom of file)


@app.route('/api/schedule', methods=['GET'])
def api_schedule_list():
    if not scheduler:
        return jsonify({'error': 'Scheduler not available'}), 503
    jobs = []
    for j in scheduler.get_jobs():
        trigger_str = ''
        try:
            trigger_str = str(j.trigger)
        except Exception:
            pass
        jobs.append({
            'id':        j.id,
            'next_run':  str(j.next_run_time) if j.next_run_time else 'paused',
            'trigger':   trigger_str,
            'enabled':   j.next_run_time is not None,
            'run_count': getattr(j, 'run_count', 0),
        })
    return jsonify({'jobs': jobs})


@app.route('/api/schedule', methods=['POST'])
def api_schedule_add():
    if not scheduler:
        return jsonify({'error': 'Scheduler not available'}), 503
    data       = request.json or {}
    cron       = data.get('cron', '').strip()
    text       = data.get('text', '').strip()
    sound_file = data.get('sound_file', '').strip()
    if not cron:
        return jsonify({'success': False, 'message': 'cron expression required'}), 400
    if not text and not sound_file:
        return jsonify({'success': False, 'message': 'text or sound_file required'}), 400
    try:
        engine = data.get('engine', 'piper')
        voice  = data.get('voice')
        preset = data.get('preset', 'normal')
        if sound_file:
            def _play_clip(sf=sound_file):
                """Play a Clips sound file over the air."""
                cfg = _clips_cfg()
                clips_dir = cfg.get('dir', CLIPS_DEFAULT_DIR)
                local_path = os.path.join(clips_dir, sf)
                # Also check S3 cache
                s3_cache = '/tmp/riggpt_clips_cache'
                cache_path = os.path.join(s3_cache, sf)
                path = local_path if os.path.exists(local_path) else (cache_path if os.path.exists(cache_path) else None)
                if not path:
                    logger.error(f'Schedule clip not found: {sf}')
                    return
                try:
                    ptt_agent = orchestrator.icom_agent
                    if orchestrator._connected:
                        ptt_agent.ptt_on()
                    import subprocess
                    dev = AUDIO_DEVICE or 'default'
                    subprocess.run(['aplay', '-D', dev, path], timeout=300, capture_output=True)
                    if orchestrator._connected:
                        ptt_agent.ptt_off()
                except Exception as e:
                    logger.error(f'Schedule clip play error: {e}')
                    try: orchestrator.icom_agent.ptt_off()
                    except Exception: pass
            job = scheduler.add_job(
                _play_clip,
                CronTrigger.from_crontab(cron),
                id=f'sched_{int(time_module.time())}'
            )
            label = sound_file
        else:
            job = scheduler.add_job(
                lambda t=text, e=engine, v=voice, p=preset: orchestrator.execute(t, engine=e, voice=v, preset=p),
                CronTrigger.from_crontab(cron),
                id=f'sched_{int(time_module.time())}'
            )
            label = text
        # Store metadata for display
        job.meta = {'text': label, 'engine': engine if not sound_file else 'clip',
                    'sound_file': sound_file, 'cron': cron}
        return jsonify({'success': True, 'job_id': job.id, 'label': label})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/sstv', methods=['POST'])
def api_sstv():
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file'}), 400
    mode        = request.form.get('mode', 'Robot36')
    vox         = request.form.get('vox', 'false').lower() == 'true'
    fskid       = request.form.get('fskid', '')
    keep_aspect = request.form.get('keep_aspect', 'false').lower() == 'true'
    _fd, img_path = tempfile.mkstemp(suffix='.png')
    os.close(_fd)
    _fd, wav_path = tempfile.mkstemp(suffix='.wav')
    os.close(_fd)
    request.files['image'].save(img_path)
    ptt_active = False
    try:
        if not image_to_sstv(img_path, wav_path, mode, vox=vox,
                              fskid=fskid, keep_aspect=keep_aspect):
            return jsonify({'success': False, 'message': 'SSTV encoding failed'}), 500
        meta = SSTV_MODE_META.get(mode, {})
        tx_sec = meta[2] if meta else '?'
        orchestrator.icom_agent.ptt_on()
        ptt_active = True
        time_module.sleep(0.3)
        orchestrator.playback_agent.play(wav_path)
        time_module.sleep(0.2)
        orchestrator.icom_agent.ptt_off()
        ptt_active = False
        log_transmission(f'[SSTV {mode}]', 'sstv', None, 'sstv',
                         tx_sec if isinstance(tx_sec, (int, float)) else 0, True)
        return jsonify({'success': True,
                        'message': f'SSTV {mode} transmitted',
                        'tx_seconds': tx_sec,
                        'resolution': f'{meta[0]}x{meta[1]}' if meta else '?',
                        'family': meta[4] if meta else '?'})
    except Exception as e:
        logger.error(f'SSTV transmit error: {e}')
        log_transmission(f'[SSTV {mode}]', 'sstv', None, 'sstv', 0, False, str(e))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if ptt_active:
            try: orchestrator.icom_agent.ptt_off()
            except Exception: pass
        for f in [img_path, wav_path]:
            if os.path.exists(f):
                try: os.remove(f)
                except Exception: pass


@app.route('/api/sstv/encode', methods=['POST'])
def api_sstv_encode():
    """Encode image to WAV and return as base64 -- no radio transmission."""
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file'}), 400
    mode        = request.form.get('mode', 'Robot36')
    vox         = request.form.get('vox', 'false').lower() == 'true'
    fskid       = request.form.get('fskid', '')
    keep_aspect = request.form.get('keep_aspect', 'false').lower() == 'true'
    _fd, img_path = tempfile.mkstemp(suffix='.png')
    os.close(_fd)
    _fd, wav_path = tempfile.mkstemp(suffix='.wav')
    os.close(_fd)
    request.files['image'].save(img_path)
    try:
        if not image_to_sstv(img_path, wav_path, mode, vox=vox,
                              fskid=fskid, keep_aspect=keep_aspect):
            return jsonify({'success': False, 'message': 'SSTV encoding failed'}), 500
        import base64
        with open(wav_path, 'rb') as f:
            wav_b64 = base64.b64encode(f.read()).decode('ascii')
        meta = SSTV_MODE_META.get(mode, [320, 240, 0, 'Color', '', ''])
        return jsonify({'success': True, 'wav_b64': wav_b64,
                        'mode': mode, 'tx_seconds': meta[2],
                        'resolution': f'{meta[0]}x{meta[1]}'})
    finally:
        for fp in [img_path, wav_path]:
            if os.path.exists(fp):
                try: os.remove(fp)
                except Exception: pass


@app.route('/api/sstv/modes')
def api_sstv_modes():
    """Return available modes with full metadata."""
    runtime_modes = []
    try:
        modes_map = _build_sstv_modes_map()
        runtime_modes = sorted(modes_map.keys())
    except Exception:
        pass
    # Merge runtime list with static metadata; fall back to static list if pysstv absent
    static_list = list(SSTV_MODE_META.keys())
    all_modes = runtime_modes if runtime_modes else static_list
    meta_out = {}
    for m in all_modes:
        if m in SSTV_MODE_META:
            w, h, s, ct, fam, desc = SSTV_MODE_META[m]
            meta_out[m] = {'width': w, 'height': h, 'tx_seconds': s,
                           'color_type': ct, 'family': fam, 'description': desc}
        else:
            meta_out[m] = {'width': 320, 'height': 240, 'tx_seconds': 0,
                           'color_type': 'Color', 'family': 'Other', 'description': m}
    return jsonify({'modes': all_modes, 'meta': meta_out})


# -------------------------------------------------------------
# Live Dashboard Routes
# -------------------------------------------------------------
@app.route('/api/dashboard/state')
def api_dashboard_state():
    with _radio_state_lock:
        return jsonify(dict(_radio_state))


@app.route('/api/dashboard/stream')
def api_dashboard_stream():
    q = queue.Queue(maxsize=30)
    with _sse_lock:
        _sse_subscribers.append(q)

    def generate():
        try:
            with _radio_state_lock:
                yield f"data: {json.dumps(_radio_state)}\n\n"
            while True:
                try:
                    yield f"data: {q.get(timeout=15)}\n\n"
                except queue.Empty:
                    yield ": keepalive\n\n"
        except GeneratorExit:
            pass
        finally:
            with _sse_lock:
                if q in _sse_subscribers:
                    _sse_subscribers.remove(q)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


# -------------------------------------------------------------
# Beacon Routes
# -------------------------------------------------------------
@app.route('/api/beacon', methods=['GET'])
def api_beacon_list():
    with _beacon_lock:
        result = []
        for bid, data in _beacons.items():
            cfg = dict(data['config'])
            cfg.update({'id': bid, 'last_tx': data.get('last_tx'),
                        'tx_count': data.get('tx_count', 0),
                        'enabled': data.get('enabled', True),
                        'active':  data.get('enabled', True)})  # alias for JS b.active
            result.append(cfg)
    return jsonify({'beacons': result})


@app.route('/api/beacon', methods=['POST'])
def api_beacon_create():
    global _beacon_count
    if not scheduler:
        return jsonify({'success': False, 'message': 'Scheduler not available'}), 503
    data       = request.json or {}
    minutes    = int(data.get('interval_minutes', 0))
    sound_file = data.get('sound_file', '').strip()
    if (not data.get('text') and not sound_file) or minutes < 1:
        return jsonify({'success': False,
                        'message': 'text (or sound_file) and interval_minutes (>=1) required'}), 400
    _beacon_count += 1
    bid = f'beacon_{_beacon_count}'
    cfg = {
        'name':       data.get('name', '') or (sound_file or f'Beacon {minutes}min'),
        'text':       data.get('text', '').strip(),
        'sound_file': sound_file,
        'phonetic':   bool(data.get('phonetic', True)),
        'interval_minutes': minutes,
        'engine':     data.get('engine', 'piper'),
        'voice':      data.get('voice'),
        'preset':     data.get('preset', 'normal'),
        'roger_beep': bool(data.get('roger_beep', True)),
        'created':    _now_utc(),
        'cw_wpm':     int(data.get('cw_wpm', 20)),
    }
    try:
        job = scheduler.add_job(
            _run_beacon, CronTrigger.from_crontab(f'*/{minutes} * * * *'),
            args=[bid], id=bid, replace_existing=True,
        )
    except Exception as e:
        return jsonify({'success': False, 'message': f'Scheduler error: {e}'}), 500
    with _beacon_lock:
        _beacons[bid] = {'config': cfg, 'job': job, 'enabled': True, 'last_tx': None, 'tx_count': 0}
    if data.get('start_now'):
        threading.Thread(target=_run_beacon, args=[bid], daemon=True).start()
    return jsonify({'success': True, 'id': bid,
                    'message': f"Beacon '{cfg['name']}' every {minutes}min"})


@app.route('/api/beacon/<bid>', methods=['DELETE'])
def api_beacon_delete(bid):
    with _beacon_lock:
        if bid not in _beacons:
            return jsonify({'success': False, 'message': 'Not found'}), 404
        try: _beacons[bid]['job'].remove()
        except Exception: pass
        del _beacons[bid]
    return jsonify({'success': True})


@app.route('/api/beacon/<bid>/fire', methods=['POST'])
def api_beacon_fire(bid):
    with _beacon_lock:
        if bid not in _beacons:
            return jsonify({'success': False, 'message': 'Not found'}), 404
    threading.Thread(target=_run_beacon, args=[bid], daemon=True).start()
    return jsonify({'success': True, 'message': 'Beacon fired'})


@app.route('/api/beacon/<bid>/pause', methods=['POST'])
def api_beacon_pause(bid):
    with _beacon_lock:
        if bid not in _beacons:
            return jsonify({'success': False, 'message': 'Not found'}), 404
        enabled = _beacons[bid].get('enabled', True)
        if enabled:
            _beacons[bid]['job'].pause(); _beacons[bid]['enabled'] = False; msg = 'Paused'
        else:
            _beacons[bid]['job'].resume(); _beacons[bid]['enabled'] = True;  msg = 'Resumed'
    return jsonify({'success': True, 'message': msg})


# -------------------------------------------------------------
# Waterfall Routes
# -------------------------------------------------------------
@app.route('/api/waterfall/preview', methods=['POST'])
def api_waterfall_preview():
    import base64
    from PIL import Image as PILImage
    # Accept either uploaded file or canned image name
    canned = request.form.get('canned', '')
    w = int(request.form.get('image_width',  128))
    h = int(request.form.get('image_height',  64))
    proc = _wf_proc_params(request.form)
    try:
        if canned and _waterfall_ok:
            from waterfall_image import CANNED_IMAGES
            fn, label = CANNED_IMAGES.get(canned, (None, None))
            if fn is None:
                return jsonify({'success': False, 'message': f'Unknown canned image: {canned}'}), 400
            # callsign can take custom text
            if canned == 'callsign':
                text = request.form.get('callsign_text', 'DE HAM')
                img = fn(size=(w*2, h*2), text=text)
            else:
                img = fn(size=(w*2, h*2))
        elif 'image' in request.files:
            img = PILImage.open(request.files['image'])
        else:
            return jsonify({'success': False, 'message': 'No image provided'}), 400

        if _waterfall_ok:
            from waterfall_image import get_processed_preview
            preview_img, hist, stats = get_processed_preview(img, w, h, scale=4, **proc)
        else:
            preview_img = img.convert('L').resize((w, h), PILImage.LANCZOS)
            hist  = [0] * 64
            stats = {}

        buf = BytesIO()
        preview_img.save(buf, format='PNG')
        b64 = base64.b64encode(buf.getvalue()).decode()
        return jsonify({
            'success': True,
            'preview': f'data:image/png;base64,{b64}',
            'histogram': hist,
            'stats': stats,
            'width': w, 'height': h,
        })
    except Exception as e:
        logger.error(f'Waterfall preview error: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/waterfall/info', methods=['POST'])
def api_waterfall_info():
    if not _waterfall_ok:
        return jsonify({'success': False, 'message': 'waterfall_image module not loaded'}), 500
    data = request.json or {}
    info = wf_info(int(data.get('image_width',128)), int(data.get('image_height',64)),
                   float(data.get('base_freq',200.0)), float(data.get('bandwidth',2400.0)),
                   float(data.get('frame_duration',0.08)))
    return jsonify({'success': True, 'info': info})


@app.route('/api/waterfall/canned', methods=['GET'])
def api_waterfall_canned():
    """List available canned test images."""
    if not _waterfall_ok:
        return jsonify({'images': []})
    from waterfall_image import CANNED_IMAGES
    return jsonify({'images': [{'id': k, 'label': v[1]} for k, v in CANNED_IMAGES.items()]})


@app.route('/api/waterfall/transmit', methods=['POST'])
def api_waterfall_transmit():
    if not _waterfall_ok:
        return jsonify({'success': False, 'message': 'waterfall_image module not loaded'}), 500

    # Accept both multipart/form-data and application/json
    _jb = request.get_json(silent=True) or {}
    def _get(key, default=''):
        return request.form.get(key, _jb.get(key, default))

    canned = _get('canned', '')
    if not canned and 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file or canned image specified. Click a canned image button first, then TX IMAGE.'}), 400

    image_width  = int(_get('image_width',   128))
    image_height = int(_get('image_height',   64))
    base_freq    = float(_get('base_freq',  200.0))
    bandwidth    = float(_get('bandwidth', 2700.0))
    frame_dur    = float(_get('frame_duration', 0.08))
    add_markers  = str(_get('add_markers', 'true')).lower() == 'true'
    proc         = _wf_proc_params(request.form) if request.form else _wf_proc_params(_jb)

    if base_freq + bandwidth > 2800:
        return jsonify({'success': False,
                        'message': f'{base_freq:.0f}+{bandwidth:.0f}={base_freq+bandwidth:.0f}Hz exceeds 2800Hz SSB passband'}), 400

    _fd, img_path = tempfile.mkstemp(suffix='.png')

    os.close(_fd)
    _fd, wav_path = tempfile.mkstemp(suffix='_waterfall.wav')
    os.close(_fd)
    try:
        # Build source image
        if canned:
            from waterfall_image import CANNED_IMAGES
            fn, label = CANNED_IMAGES.get(canned, (None, None))
            if fn is None:
                return jsonify({'success': False, 'message': f'Unknown canned: {canned}'}), 400
            if canned == 'callsign':
                text = request.form.get('callsign_text', 'DE HAM')
                img = fn(size=(image_width*2, image_height*2), text=text)
            else:
                img = fn(size=(image_width*2, image_height*2))
            img.save(img_path)
        else:
            request.files['image'].save(img_path)

        t0 = time_module.time()
        wav_path = image_to_waterfall_wav(
            img_path, wav_path,
            image_width=image_width, image_height=image_height,
            base_freq=base_freq, bandwidth=bandwidth,
            frame_duration=frame_dur, add_markers=add_markers,
            **proc,
        )
        info = wf_info(image_width, image_height, base_freq, bandwidth, frame_dur)
        ptt_active = False
        try:
            orchestrator.icom_agent.ptt_on()
            ptt_active = True
            time_module.sleep(0.3)
            played = orchestrator.playback_agent.play(wav_path, normalize=False)
            time_module.sleep(0.2)
            orchestrator.icom_agent.ptt_off()
            ptt_active = False
        finally:
            if ptt_active:
                try: orchestrator.icom_agent.ptt_off()
                except Exception: pass
        duration = round(time_module.time() - t0, 1)
        label = canned if canned else 'upload'
        log_transmission(f'[WATERFALL {image_width}x{image_height} {label}]',
                         'waterfall', None, 'waterfall', duration, True)
        return jsonify({'success': True,
                        'message': f'Waterfall transmitted ({info["total_duration_s"]})',
                        'info': info, 'duration': duration})
    except Exception as e:
        logger.error(f'Waterfall transmit error: {e}')
        log_transmission(f'[WATERFALL]', 'waterfall', None, 'waterfall', 0, False, str(e))
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        for path in [img_path, wav_path]:
            if path and os.path.exists(path):
                try: os.remove(path)
                except Exception: pass


def _wf_proc_params(form):
    """Extract image processing params from request.form."""
    def fb(k, d): return float(form.get(k, d))
    def ib(k, d): return int(form.get(k, d))
    def bb(k):    return form.get(k, 'false').lower() == 'true'
    return dict(
        brightness  = fb('brightness',  1.0),
        contrast    = fb('contrast',    1.5),
        gamma       = fb('gamma',       0.7),
        sharpen     = fb('sharpen',     0.0),
        equalize    = bb('equalize'),
        dither      = bb('dither'),
        invert      = bb('invert'),
        tone_curve  = form.get('tone_curve', 'gamma'),
        noise_floor = fb('noise_floor', 0.03),
        black_point = ib('black_point', 0),
        white_point = ib('white_point', 255),
        flip_v      = bb('flip_v'),
        flip_h      = bb('flip_h'),
    )


# -------------------------------------------------------------
# Hardware Interrogation & Diagnostics
# -------------------------------------------------------------
@app.route('/api/radio/probe')
def api_radio_probe():
    """Full hardware diagnostic -- serial ports, radio response, audio devices."""
    result = {
        'config': {
            'serial_port':   orchestrator.icom_agent.port,
            'baud_rate':     orchestrator.icom_agent.baudrate,
            'ci_v_address':  f'0x{orchestrator.icom_agent.ci_v_address:02X}',
            'audio_device':  AUDIO_DEVICE,
        },
        'serial': {
            'open':      bool(orchestrator.icom_agent.serial_conn and
                              orchestrator.icom_agent.serial_conn.is_open),
            'connected': orchestrator._connected,
        },
        'available_ports': IcomSerialAgent.score_ports(),
        'radio_probe':     None,
        'audio':           {},
    }

    # Audio devices
    try:
        r  = subprocess.run(['aplay', '-l'], capture_output=True, text=True, timeout=5)
        r2 = subprocess.run(['aplay', '-L'], capture_output=True, text=True, timeout=5)
        result['audio'] = {
            'current_device':  AUDIO_DEVICE,
            'hardware_cards':  r.stdout.strip(),
            'device_list':     [l for l in r2.stdout.splitlines()
                                 if not l.startswith(' ')],
        }
    except Exception as e:
        result['audio']['error'] = str(e)

    # Radio probe
    if result['serial']['open']:
        result['radio_probe'] = orchestrator.icom_agent.probe_radio()
    else:
        # Try to connect first
        scored = result['available_ports']
        if scored:
            best_port = scored[0]['device']
            logger.info(f"Probe: attempting connect to {best_port}")
            if orchestrator.connect(best_port):
                result['radio_probe']    = orchestrator.icom_agent.probe_radio()
                result['auto_connected'] = best_port
                result['serial']['open'] = True

    return jsonify(result)


@app.route('/api/radio/ptt_test', methods=['POST'])
def api_radio_ptt_test():
    """Fire PTT for a specified duration -- isolates PTT from audio for testing.
    If the serial port is not already open, attempts to connect using the
    port/baud/ci_v_address values from the request body (or saved settings).
    This mirrors the behaviour of the connect button so the PTT test works
    even if the page was loaded before auto-connect finished.
    POST: { duration?, port?, baud?, ci_v_address? }
    """
    data     = request.json or {}
    duration = float(data.get('duration', 1.0))
    duration = max(0.1, min(duration, 10.0))

    agent = orchestrator.icom_agent

    # If not connected, try to open the serial port using caller-supplied or
    # saved settings so the PTT test doesn't require a prior /api/connect call.
    if not (agent.serial_conn and agent.serial_conn.is_open):
        port   = (data.get('port') or
                  _app_settings.get('serial_port', SERIAL_PORT) or
                  SERIAL_PORT)
        baud   = int(data.get('baud',
                              _app_settings.get('baud_rate', BAUD_RATE)))
        ci_v_raw = data.get('ci_v_address',
                            _app_settings.get('ci_v_address', hex(CI_V_ADDRESS)))
        try:
            ci_v = int(str(ci_v_raw), 0)
        except (ValueError, TypeError):
            ci_v = CI_V_ADDRESS
        logger.info(f'ptt_test: serial not open -- attempting connect: '
                    f'{port} @ {baud} CI-V 0x{ci_v:02X}')
        agent.ci_v_address = ci_v
        try:
            ok = orchestrator.connect(port, baud)
        except Exception as e:
            ok = False
            logger.warning(f'ptt_test: connect exception: {e}')
        if not ok or not (agent.serial_conn and agent.serial_conn.is_open):
            return jsonify({
                'success': False,
                'message': (f'Serial port {port!r} could not be opened. '
                            f'Check port, baud rate, and that the radio is '
                            f'connected and powered on.'),
            }), 400

    def _do_ptt():
        agent.ptt_on()
        time_module.sleep(duration)
        agent.ptt_off()
    threading.Thread(target=_do_ptt, daemon=True, name='ptt-test').start()
    port_name = agent.port or SERIAL_PORT
    return jsonify({'success': True,
                    'message': f'PTT keyed for {duration:.1f}s on {port_name}'})


@app.route('/api/debug/civ', methods=['GET', 'POST'])
def api_debug_civ():
    """CI-V address auto-scanner.
    GET  -- scans all common IC-7610 addresses and returns which responds.
    POST -- sends a raw read-frequency command to the current address and returns raw bytes.
    """
    agent = orchestrator.icom_agent
    if not agent.serial_conn or not agent.serial_conn.is_open:
        return jsonify({'success': False, 'message': 'Serial port not open -- connect first'}), 400

    if request.method == 'GET':
        # Temporarily set log level to DEBUG for this scan
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        results = {}
        # IC-7610 commonly uses 0x80 (factory default) or 0x98 (some firmware)
        # Controller address is always 0xE0 on the PC side
        candidates = [0x80, 0x98, 0x88, 0x90, 0x94, 0xA0, 0x70, 0x68, 0x60]
        original   = agent.ci_v_address
        try:
            for addr in candidates:
                agent.ci_v_address = addr
                # Flush any stale bytes
                try: agent.serial_conn.reset_input_buffer()
                except Exception: pass
                time_module.sleep(0.05)
                freq = agent.read_frequency()
                responded = freq is not None
                results[f'0x{addr:02X}'] = {
                    'responded': responded,
                    'frequency_hz': freq,
                    'frequency_mhz': round(freq/1e6,4) if freq else None,
                }
                logger.info(f"CI-V scan 0x{addr:02X}: {'RESPONDED freq={}'.format(freq) if responded else 'no response'}")
                if responded:
                    break   # found it -- leave ci_v_address set to the working one
            else:
                # Nothing responded -- restore original
                agent.ci_v_address = original
        finally:
            logger.setLevel(old_level)

        working = [addr for addr, r in results.items() if r['responded']]
        return jsonify({
            'success': True,
            'current_address': f'0x{agent.ci_v_address:02X}',
            'scan_results': results,
            'working_addresses': working,
            'message': (f"Found working address: {working[0]}" if working
                        else "No CI-V response from any address -- check baud rate and cable"),
        })

    else:  # POST -- raw read-frequency with current address, return raw bytes
        old_level = logger.level
        logger.setLevel(logging.DEBUG)
        try:
            agent.serial_conn.reset_input_buffer()
            resp = agent.send_command(0x03)   # read frequency
            if resp:
                raw_hex = ' '.join(f'{b:02X}' for b in resp)
            else:
                raw_hex = None
            freq = agent.read_frequency() if resp else None
            return jsonify({
                'success': resp is not None,
                'current_address': f'0x{agent.ci_v_address:02X}',
                'controller_address': f'0x{agent.controller_address:02X}',
                'raw_response_hex': raw_hex,
                'decoded_frequency_hz': freq,
                'port': agent.port,
                'baud': agent.baudrate,
                'message': f"freq={freq}" if freq else "No response",
            })
        finally:
            logger.setLevel(old_level)


@app.route('/api/debug/log_level', methods=['POST'])
def api_debug_log_level():
    """Temporarily change log verbosity. POST {level: 'DEBUG'|'INFO'|'WARNING'}"""
    data  = request.json or {}
    level = data.get('level', 'DEBUG').upper()
    lvl   = getattr(logging, level, None)
    if lvl is None:
        return jsonify({'success': False, 'message': f'Unknown level: {level}'}), 400
    logger.setLevel(lvl)
    logger.info(f"Log level changed to {level}")
    return jsonify({'success': True, 'level': level})


@app.route('/api/audio/devices')
def api_audio_devices():
    try:
        r  = subprocess.run(['aplay', '-L'], capture_output=True, text=True, timeout=5)
        r2 = subprocess.run(['aplay', '-l'], capture_output=True, text=True, timeout=5)
        return jsonify({'current_device': AUDIO_DEVICE,
                        'devices_list':   r.stdout.strip().splitlines(),
                        'hardware_cards': r2.stdout.strip()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/audio/test', methods=['POST'])
def api_audio_test():
    data   = request.json or {}
    device = data.get('device', AUDIO_DEVICE)
    _fd, test_wav = tempfile.mkstemp(suffix='_test.wav')
    os.close(_fd)
    try:
        subprocess.run(['sox', '-n', '-r', '44100', '-b', '16', test_wav,
                        'synth', '1.0', 'sine', '1000', 'vol', '0.5'],
                       check=True, capture_output=True, timeout=10)
        cmd = ['aplay']
        if device:
            cmd += ['-D', device]
        cmd.append(test_wav)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            return jsonify({'success': True, 'message': f'Test tone played on {device}'})
        return jsonify({'success': False, 'message': result.stderr.strip()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    finally:
        if os.path.exists(test_wav):
            try: os.remove(test_wav)
            except Exception: pass


# -------------------------------------------------------------
# Radio Control -- Frequency / Mode
# -------------------------------------------------------------
@app.route('/api/radio/frequency', methods=['GET'])
def api_radio_get_frequency():
    freq = orchestrator.icom_agent.read_frequency()
    if freq is None:
        return jsonify({'success': False, 'message': 'No response from radio'}), 503
    return jsonify({'success': True, 'frequency_hz': freq,
                    'frequency_mhz': round(freq / 1e6, 6)})


@app.route('/api/radio/frequency', methods=['POST'])
def api_radio_set_frequency():
    data = request.json or {}
    freq = data.get('frequency_hz') or data.get('frequency_mhz')
    if freq is None:
        return jsonify({'success': False, 'message': 'frequency_hz or frequency_mhz required'}), 400
    if data.get('frequency_mhz'):
        freq = int(float(data['frequency_mhz']) * 1e6)
    freq = int(freq)
    if not (30000 <= freq <= 74800000):
        return jsonify({'success': False, 'message': f'Frequency {freq} Hz out of range (30 kHz - 74.8 MHz)'}), 400
    ok = orchestrator.icom_agent.set_frequency(freq)
    return jsonify({'success': ok, 'frequency_hz': freq,
                    'frequency_mhz': round(freq / 1e6, 6),
                    'message': f'Tuned to {freq/1e6:.4f} MHz' if ok else 'Radio did not ACK'})


@app.route('/api/radio/mode', methods=['GET'])
def api_radio_get_mode():
    mode = orchestrator.icom_agent.read_mode()
    if mode is None:
        return jsonify({'success': False, 'message': 'No response from radio'}), 503
    return jsonify({'success': True, 'mode': mode})


@app.route('/api/radio/mode', methods=['POST'])
def api_radio_set_mode():
    data   = request.json or {}
    mode   = (data.get('mode') or '').upper().strip()
    filt   = int(data.get('filter', 1))
    valid  = ['LSB','USB','AM','CW','RTTY','FM','WFM','CW-R','RTTY-R','DV','USB-D','LSB-D']
    if mode not in valid:
        return jsonify({'success': False,
                        'message': f'Unknown mode: {mode}. Valid: {valid}'}), 400
    ok = orchestrator.icom_agent.set_mode(mode, filt)
    return jsonify({'success': ok, 'mode': mode,
                    'message': f'Mode set to {mode}' if ok else 'Radio did not ACK'})


# -------------------------------------------------------------
# Audio Level Calibration
# -------------------------------------------------------------
@app.route('/api/audio/calibrate', methods=['POST'])
def api_audio_calibrate():
    """
    Transmit a calibration tone and measure ALC.
    Iterates aplay volume / sox gain to find a level where ALC is
    just below the threshold (target ALC < 60/255).

    Returns the recommended sox gain value and ALC readings.
    """
    data       = request.json or {}
    target_alc = int(data.get('target_alc', 50))    # 0-255, keep below this
    max_iter   = int(data.get('max_iterations', 8))
    tone_freq  = int(data.get('tone_hz', 1000))
    tone_dur   = float(data.get('tone_duration', 0.5))

    agent = orchestrator.icom_agent
    if not agent.serial_conn or not agent.serial_conn.is_open:
        return jsonify({'success': False, 'message': 'Radio not connected - use CONNECT button'})

    log      = []
    gain_db  = 0.0    # start at 0 dB, reduce if ALC is too high
    step     = 3.0    # dB steps
    best     = None   # (gain_db, alc)

    def _make_tone(gain):
        _fd, path = tempfile.mkstemp(suffix='_cal.wav')
        os.close(_fd)
        try:
            subprocess.run(
                ['sox', '-n', '-r', '44100', '-b', '16', '-c', '1', path,
                 'synth', str(tone_dur), 'sine', str(tone_freq),
                 'gain', str(gain)],
                check=True, capture_output=True
            )
        except Exception:
            try: os.remove(path)
            except Exception: pass
            raise
        return path

    def _play_and_measure(tone_path):
        """PTT on, play tone, read ALC during playback, PTT off."""
        alc_readings = []
        agent.ptt_on()
        time_module.sleep(0.15)

        play_thread_done = threading.Event()
        def _play():
            cmd = ['aplay']
            if AUDIO_DEVICE and AUDIO_DEVICE != 'default':
                cmd += ['-D', AUDIO_DEVICE]
            cmd.append(tone_path)
            subprocess.run(cmd, capture_output=True, timeout=10)
            play_thread_done.set()

        t = threading.Thread(target=_play, daemon=True)
        t.start()

        # Sample ALC every 50 ms while tone plays
        deadline = time_module.time() + tone_dur + 0.3
        while time_module.time() < deadline and not play_thread_done.is_set():
            alc = agent.read_alc()
            if alc is not None:
                alc_readings.append(alc)
            time_module.sleep(0.05)

        play_thread_done.wait(timeout=2)
        time_module.sleep(0.1)
        agent.ptt_off()
        return int(sum(alc_readings) / len(alc_readings)) if alc_readings else None

    try:
        for i in range(max_iter):
            tone_path = _make_tone(gain_db)
            alc       = _play_and_measure(tone_path)
            os.remove(tone_path)

            entry = {'iteration': i+1, 'gain_db': round(gain_db, 1),
                     'alc_raw': alc, 'alc_pct': round((alc or 0) / 255 * 100)}
            log.append(entry)
            logger.info(f"Calibration iter {i+1}: gain={gain_db:+.1f} dB, ALC={alc}")

            if alc is None:
                return jsonify({'success': False, 'message': 'Radio not responding ALC reads -- check CI-V', 'log': log})

            if alc < target_alc:
                best = (gain_db, alc)
                # Try nudging up slightly to find a tighter upper bound
                if alc < target_alc * 0.5 and i < max_iter - 1:
                    gain_db += step / 2
                else:
                    break
            else:
                gain_db -= step
                step = max(step * 0.6, 0.5)

        if best is None:
            best = (gain_db, alc)

        rec_gain, rec_alc = best
        msg = (f"Recommended sox gain: {rec_gain:+.1f} dB  "
               f"(ALC {rec_alc}/{target_alc} target, {round(rec_alc/255*100)}%)")
        logger.info(f"Calibration complete: {msg}")
        return jsonify({
            'success':           True,
            'recommended_gain_db': round(rec_gain, 1),
            'alc_raw':           rec_alc,
            'alc_target':        target_alc,
            'alc_pct':           round(rec_alc / 255 * 100),
            'message':           msg,
            'log':               log,
            'usage':             f"Add gain {rec_gain:+.1f} dB in Sox audio effects, or set AUDIO_GAIN_DB={rec_gain:.1f}",
        })
    except Exception as e:
        logger.error(f"Calibration error: {e}")
        try: agent.ptt_off()
        except Exception: pass
        return jsonify({'success': False, 'message': str(e), 'log': log}), 500


@app.route('/api/audio/alc', methods=['GET'])
def api_audio_alc():
    """Instant ALC reading without transmitting."""
    alc = orchestrator.icom_agent.read_alc()
    rf  = orchestrator.icom_agent.read_rf_power()
    return jsonify({
        'alc_raw':  alc,
        'alc_pct':  round((alc or 0) / 255 * 100),
        'rf_raw':   rf,
        'rf_pct':   round((rf or 0) / 255 * 100),
    })


# -------------------------------------------------------------
# API Integration Management Routes
# -------------------------------------------------------------

@app.route('/api/integrations', methods=['GET'])
def api_integrations_list():
    """Return registry of all provider configs (no secrets in response)."""
    if not _api_keys_ok:
        return jsonify({'error': 'api_keys module not loaded', 'providers': []}), 500
    return jsonify({'providers': _api_keys.get_registry_for_api()})


@app.route('/api/integrations/<provider_id>', methods=['GET'])
def api_integrations_get(provider_id):
    """Get config for a single provider (masked secrets)."""
    if not _api_keys_ok:
        return jsonify({'error': 'api_keys module not loaded'}), 500
    registry = {p['id']: p for p in _api_keys.get_registry_for_api()}
    if provider_id not in registry:
        return jsonify({'error': f'Unknown provider: {provider_id}'}), 404
    return jsonify(registry[provider_id])


@app.route('/api/integrations/<provider_id>', methods=['POST'])
def api_integrations_save(provider_id):
    """Save field values for a provider. Password fields are obfuscated at rest."""
    if not _api_keys_ok:
        return jsonify({'success': False, 'error': 'api_keys module not loaded'}), 500
    data = request.json or {}
    # Strip out any meta-keys
    fields = {k: v for k, v in data.items() if not k.startswith('_')}
    ok = _api_keys.set_provider_config(provider_id, fields)
    if ok:
        # Reload ElevenLabs key immediately
        global ELEVENLABS_API_KEY
        ELEVENLABS_API_KEY = _get_elevenlabs_key()
        # Re-apply Discord config if that provider was just updated
        if provider_id == 'discord':
            threading.Thread(target=_discord_apply_config, daemon=True,
                             name='discord-cfg-apply').start()
        logger.info(f"Integration config saved: {provider_id}")
    return jsonify({'success': ok,
                    'message': f'{provider_id} configuration saved' if ok else 'Save failed -- check server permissions'})


@app.route('/api/integrations/<provider_id>', methods=['DELETE'])
def api_integrations_delete(provider_id):
    """Clear all stored config for a provider."""
    if not _api_keys_ok:
        return jsonify({'success': False}), 500
    ok = _api_keys.delete_provider_config(provider_id)
    if ok:
        global ELEVENLABS_API_KEY
        ELEVENLABS_API_KEY = _get_elevenlabs_key()
    return jsonify({'success': ok})


@app.route('/api/integrations/<provider_id>/test', methods=['POST'])
def api_integrations_test(provider_id):
    """Run connectivity test for a provider using current config."""
    if not _api_keys_ok:
        return jsonify({'success': False, 'message': 'api_keys module not loaded'}), 500
    ok, msg = _api_keys.test_provider(provider_id)
    safe_msg = msg.encode('ascii', errors='replace').decode('ascii') if msg else ''
    logger.info(f"Integration test {provider_id}: {'OK' if ok else 'FAIL'} -- {safe_msg}")
    return jsonify({'success': ok, 'message': safe_msg})


@app.route('/api/voices/espeak')
def api_voices_espeak():
    """Return common espeak-ng voice identifiers."""
    voices = [
        {'id': 'en-us',     'name': 'English (US)'},
        {'id': 'en',        'name': 'English (UK)'},
        {'id': 'en-us+m1',  'name': 'English (US) Male 1'},
        {'id': 'en-us+m2',  'name': 'English (US) Male 2'},
        {'id': 'en-us+m3',  'name': 'English (US) Male 3'},
        {'id': 'en-us+f1',  'name': 'English (US) Female 1'},
        {'id': 'en-us+f2',  'name': 'English (US) Female 2'},
        {'id': 'en+m1',     'name': 'English (UK) Male 1'},
        {'id': 'en+f1',     'name': 'English (UK) Female 1'},
        {'id': 'en-us+croak', 'name': 'Croak'},
        {'id': 'en-us+whisper', 'name': 'Whisper'},
    ]
    return jsonify({'voices': voices})


@app.route('/api/voices/openai')
def api_voices_openai():
    """OpenAI TTS voices."""
    voices = [
        {'id': 'alloy',   'name': 'Alloy'},
        {'id': 'echo',    'name': 'Echo'},
        {'id': 'fable',   'name': 'Fable'},
        {'id': 'onyx',    'name': 'Onyx'},
        {'id': 'nova',    'name': 'Nova'},
        {'id': 'shimmer', 'name': 'Shimmer'},
    ]
    return jsonify({'voices': voices})


@app.route('/api/voices/speechify')
def api_speechify_voices():
    agent = orchestrator.speechify_agent
    key   = SpeechifyTTSAgent._get_key()
    if not key:
        return jsonify({'error': 'Speechify API key not configured', 'voices': {}})
    return jsonify({'voices': agent.get_voices()})


@app.route('/api/voices/fastkoko')
def api_fastkoko_voices():
    agent = orchestrator.fastkoko_agent
    url   = FastKokoTTSAgent._get_url()
    if not url:
        return jsonify({'error': 'FastKoko URL not configured', 'voices': []})
    voices = agent.get_voices()
    if not voices:
        return jsonify({'error': f'No voices returned from {url}', 'voices': []})
    return jsonify({'voices': voices})


@app.route('/api/voices/edge')
def api_voices_edge():
    return jsonify({'voices': EdgeTTSAgent.VOICES})


@app.route('/api/voices/gtts')
def api_voices_gtts():
    return jsonify({'voices': GTTSAgent.VOICES})


@app.route('/api/voices/pyttsx3')
def api_voices_pyttsx3():
    return jsonify({'voices': Pyttsx3Agent.get_voices()})


@app.route('/api/engines/status')
def api_engines_status():
    """Check which TTS engines are available on this system."""
    status = {}
    for mod, eng in [('edge_tts','edge'),('gtts','gtts'),('pyttsx3','pyttsx3')]:
        try:
            __import__(mod)
            status[eng] = 'ok'
        except ImportError:
            status[eng] = 'not installed'
    status['espeak']     = 'ok'
    status['piper']      = 'ok'
    status['elevenlabs'] = ('ok' if ELEVENLABS_API_KEY else 'needs API key')
    status['speechify']  = 'needs API key'
    status['openai']     = 'needs API key'
    status['fastkoko']   = ('ok' if FastKokoTTSAgent._get_url() else 'no URL configured')
    return jsonify(status)


# -------------------------------------------------------------
# Radio Control -- Levels & Functions (Dashboard knobs)
# -------------------------------------------------------------

@app.route('/api/radio/control', methods=['POST'])
def api_radio_control():
    """Set any radio control: af_gain, rf_gain, sql, rf_power, nr, nb, att, preamp, agc, split, vfo, vfo_swap, vfo_a_to_b."""
    data  = request.json or {}
    agent = orchestrator.icom_agent
    if not agent.serial_conn or not agent.serial_conn.is_open:
        return jsonify({'success': False, 'message': 'Radio not connected - use CONNECT button'})

    results = {}
    LEVEL_MAP = {'af_gain': 0x01, 'rf_gain': 0x02, 'sql': 0x03,
                 'mic_gain': 0x0B, 'rf_power': 0x0A, 'nr_level': 0x06}
    FUNC_MAP  = {'nr': 0x40, 'nb': 0x22, 'comp': 0x03, 'mon': 0x09}

    for key, val in data.items():
        if key in LEVEL_MAP:
            ok = agent.set_level(LEVEL_MAP[key], int(val))
            results[key] = 'ok' if ok else 'nak'
        elif key in FUNC_MAP:
            ok = agent.set_function(FUNC_MAP[key], bool(val))
            results[key] = 'ok' if ok else 'nak'
        elif key == 'att':
            ok = agent.set_att(int(val))
            results[key] = 'ok' if ok else 'nak'
        elif key == 'preamp':
            ok = agent.set_preamp(int(val))
            results[key] = 'ok' if ok else 'nak'
        elif key == 'agc':
            ok = agent.set_agc(int(val))
            results[key] = 'ok' if ok else 'nak'
        elif key == 'split':
            ok = agent.set_split(bool(val))
            results[key] = 'ok' if ok else 'nak'
        elif key == 'vfo':
            ok = agent.set_vfo(val)
            results[key] = 'ok' if ok else 'nak'
        elif key == 'vfo_swap':
            ok = agent.vfo_swap()
            results['vfo_swap'] = 'ok' if ok else 'nak'
        elif key == 'vfo_a_to_b':
            ok = agent.vfo_a_to_b()
            results['vfo_a_to_b'] = 'ok' if ok else 'nak'
        elif key == 'ant':
            ok = agent.set_antenna(int(val))
            results['ant'] = 'ok' if ok else 'nak'

    return jsonify({'success': True, 'results': results})


# -------------------------------------------------------------
# TX Terminate Route
# -------------------------------------------------------------
@app.route('/api/tx/terminate', methods=['POST'])
def api_tx_terminate():
    global _active_tx_proc
    killed = False
    # Kill active aplay process
    if _active_tx_proc is not None:
        try:
            _active_tx_proc.terminate()
            killed = True
            logger.info('TX terminated by user (aplay SIGTERM)')
        except Exception as e:
            logger.warning(f'Terminate aplay error: {e}')
    # Also drop PTT regardless
    try:
        if orchestrator.icom_agent and orchestrator.icom_agent.serial_conn \
                and orchestrator.icom_agent.serial_conn.is_open:
            orchestrator.icom_agent.ptt_off()
            logger.info('PTT forced off by terminate')
    except Exception as e:
        logger.warning(f'PTT off error during terminate: {e}')
    return jsonify({'success': True, 'killed': killed,
                    'message': 'Transmission terminated' if killed else 'No active TX to terminate'})


# -------------------------------------------------------------
# WAV Cache and Log Replay Routes
# -------------------------------------------------------------
@app.route('/api/log/wav/<int:tx_id>')
def api_log_wav(tx_id):
    import base64
    wav_path = os.path.join(WAV_CACHE_DIR, f'{tx_id}.wav')
    if not os.path.exists(wav_path):
        return jsonify({'success': False, 'message': 'No cached audio for this entry'}), 404
    try:
        with open(wav_path, 'rb') as f:
            wav_b64 = base64.b64encode(f.read()).decode('ascii')
        size_kb = round(os.path.getsize(wav_path) / 1024, 1)
        return jsonify({'success': True, 'wav_b64': wav_b64,
                        'tx_id': tx_id, 'size_kb': size_kb})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/log/wav/<int:tx_id>', methods=['DELETE'])
def api_log_wav_delete(tx_id):
    wav_path = os.path.join(WAV_CACHE_DIR, f'{tx_id}.wav')
    try:
        if os.path.exists(wav_path):
            os.remove(wav_path)
        conn = sqlite3.connect(DB_PATH)
        conn.execute('UPDATE transmissions SET wav_cached=0 WHERE id=?', (tx_id,))
        conn.commit(); conn.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# -------------------------------------------------------------
# Audio File Playback Route
# -------------------------------------------------------------
@app.route('/api/audio/play_file', methods=['POST'])
def api_audio_play_file():
    data  = request.json or {}
    fname = data.get('file', '').strip()
    if not fname:
        return jsonify({'success': False, 'message': 'No file specified'}), 400

    # Special token 'taco_bell' maps to the configurable gong path
    if fname == 'taco_bell':
        fpath = get_gong_path()
    else:
        # Restrict to files inside the agent directory to prevent path traversal
        fpath = os.path.join('/opt/riggpt', os.path.basename(fname))

    if not os.path.exists(fpath):
        logger.warning(f'play_file: file not found: {fpath!r}')
        return jsonify({'success': False, 'message': f'File not found: {fpath}'}), 404

    # Drop duplicate requests while a play is already in progress.
    # Rapid clicks stack concurrent aplay processes that all race for
    # the same ALSA device and fail with "Device or resource busy".
    if not _play_file_lock.acquire(blocking=False):
        logger.info('play_file: device busy (another play in progress) - skipping duplicate')
        return jsonify({'success': True, 'message': 'Already playing'}), 200

    def _play():
        try:
            # Mirror the transmit path: try configured device -> 'default' -> bare aplay.
            devices_to_try = []
            if AUDIO_DEVICE and AUDIO_DEVICE != 'default':
                devices_to_try.append(AUDIO_DEVICE)
            devices_to_try.append('default')
            devices_to_try.append(None)   # bare aplay with no -D flag

            for dev in devices_to_try:
                try:
                    cmd = ['aplay']
                    if dev:
                        cmd += ['-D', dev]
                    cmd.append(fpath)
                    logger.info(f'play_file: aplay device={dev or "system-default"} file={fpath!r}')
                    result = subprocess.run(cmd, capture_output=True, timeout=30)
                    if result.returncode == 0:
                        logger.info(f'play_file: aplay OK (device={dev or "system-default"})')
                        return   # success - stop trying
                    err = result.stderr.decode('utf-8', errors='replace').strip()
                    logger.warning(f'play_file: aplay failed (device={dev or "system-default"}) rc={result.returncode}: {err}')
                except FileNotFoundError:
                    logger.error('play_file: aplay not found - is alsa-utils installed?')
                    return
                except subprocess.TimeoutExpired:
                    logger.warning(f'play_file: aplay timed out (device={dev or "system-default"})')
                except Exception as e:
                    logger.warning(f'play_file: aplay exception (device={dev or "system-default"}): {e}')

            logger.error(f'play_file: all aplay attempts failed for {fpath!r}')
        finally:
            _play_file_lock.release()

    threading.Thread(target=_play, daemon=True, name='gong-play').start()
    return jsonify({'success': True, 'message': f'Playing {os.path.basename(fpath)}'})


# -------------------------------------------------------------
# Application Settings
# -------------------------------------------------------------
@app.route('/api/settings', methods=['GET'])
def api_settings_get():
    """Return current application settings."""
    return jsonify(_app_settings)

@app.route('/api/settings', methods=['POST'])
def api_settings_post():
    """Update application settings. Merges patch into current settings."""
    global _app_settings
    patch = request.json or {}
    # Allowed setting keys (whitelist to avoid arbitrary writes)
    allowed = {
        'gong_path', 'ollama_url', 'ollama_model', 'ollama_enabled',
        'ai_persona', 'ai_temp', 'ai_max_tokens', 'ai_mode',
        'serial_port', 'baud_rate', 'ci_v_address',
        'radio_model',
        # AI tab TX voice
        'ai_tx_engine', 'ai_tx_voice', 'ai_auto_tx',
        # Acid Trip agent presets
        'trip_a_emoji', 'trip_a_engine', 'trip_a_voice',
        'trip_a_provider', 'trip_a_model', 'trip_a_model_sel',
        'trip_a_persona', 'trip_a_canon', 'trip_a_seed',
        'trip_b_emoji', 'trip_b_engine', 'trip_b_voice',
        'trip_b_provider', 'trip_b_model', 'trip_b_model_sel',
        'trip_b_persona', 'trip_b_canon', 'trip_b_seed',
        'trip_turns', 'trip_delay', 'trip_max_tok', 'trip_temp',
        # Conversational spacing
        'trip_gap_min', 'trip_gap_max', 'trip_hesitate',
        'trip_discord_influence', 'trip_discord_lookback', 'trip_discord_lookback_every',
        # Transmit tab defaults
        'tx_engine', 'tx_voice', 'tx_delay', 'tx_repeat',
        # Memory / Qdrant
        'memory_enabled', 'memory_qdrant_host', 'memory_embed_model',
        # Alexa mode
        'alexa_enabled', 'alexa_engine', 'alexa_voice',
        'alexa_model', 'alexa_trigger', 'alexa_max_tok',
        # Clips / Media Player
        'clips_dir', 'clips_poll_interval',
        'clips_s3_enabled', 'clips_s3_bucket',
        'clips_s3_region', 'clips_s3_prefix',
        # Discord monitor
        'discord_inject_target', 'discord_inject_format',
        # Audio device
        'audio_device',
        # Waterfall ART
        'wf_bw', 'wf_sideband', 'wf_contrast', 'wf_dur',
        # SSTV
        'sstv_vox',
        # Beacon form defaults
        'bcn_interval', 'bcn_repeat', 'bcn_engine',
        # Special Ops
        'numbers_station_interval', 'numbers_station_engine',
        'solar_autotx_enabled', 'solar_kindex_threshold',
        'mystery_window_start', 'mystery_window_end',
        'autoid_callsign', 'autoid_interval', 'autoid_engine',
        # Pirate Broadcast
        'pirate_interval', 'pirate_engine',
    }
    updated = {}
    for k, v in patch.items():
        if k in allowed:
            _app_settings[k] = str(v).strip()
            updated[k] = _app_settings[k]
    if updated:
        _save_app_settings(_app_settings)
        log_event('INFO', 'SETTINGS', f'Updated settings: {list(updated.keys())}')
    return jsonify({'success': True, 'updated': updated, 'settings': _app_settings})


@app.route('/api/config/export', methods=['GET'])
def api_config_export():
    """Export the full operator configuration as a self-contained JSON backup.

    Query params:
      ?include_keys=true   - export plaintext API keys (default: masked)
      ?include_schedules=true - include scheduled jobs (default: true)

    The bundle captures EVERY user-configurable value:
      settings:    all _app_settings keys (gong_path, AI config, serial, etc.)
      api_keys:    all provider fields (plaintext or masked per include_keys)
      beacons:     all saved beacon definitions
      schedules:   all APScheduler jobs tagged with config metadata
      ui_presets:  Acid Trip agent config, AI TX voice, per-UI preferences
    """
    import copy
    include_keys = request.args.get('include_keys', 'false').lower() == 'true'

    bundle = {
        '__version__':       VERSION,
        '__format__':        'riggpt-config',
        '__exported_at__':   datetime.now(timezone.utc).isoformat(),
        '__keys_masked__':   not include_keys,
        'settings':          copy.deepcopy(_app_settings),
        'api_keys':          {},
        'beacons':           [],
        'schedules':         [],
        'ui_presets':        {},
    }

    # -- API keys ---------------------------------------------
    if _api_keys_ok:
        try:
            raw_keys = _api_keys._load_keys()
            for pid, reg in _api_keys.PROVIDER_REGISTRY.items():
                stored = raw_keys.get(pid, {})
                bundle['api_keys'][pid] = {}
                for field_id, field_def in reg.get('fields', {}).items():
                    val = stored.get(field_id, '')
                    if field_def.get('type') == 'password' and val and not include_keys:
                        # Show last 4 chars so user can verify which key is stored
                        bundle['api_keys'][pid][field_id] = ('****' + val[-4:]) if len(val) > 4 else '****'
                    else:
                        bundle['api_keys'][pid][field_id] = val
        except Exception as e:
            logger.warning(f'Config export: api_keys read error: {e}')

    # -- Beacons ----------------------------------------------
    try:
        beacons_resp = api_beacon_list()
        beacons_data = beacons_resp.get_json() if hasattr(beacons_resp, 'get_json') else {}
        bundle['beacons'] = beacons_data.get('beacons', [])
    except Exception as e:
        logger.warning(f'Config export: beacons error: {e}')

    # -- Scheduled jobs ---------------------------------------
    try:
        sched_resp = api_schedule_list()
        sched_data = sched_resp.get_json() if hasattr(sched_resp, 'get_json') else {}
        bundle['schedules'] = sched_data.get('jobs', [])
    except Exception as e:
        logger.warning(f'Config export: schedules error: {e}')

    # -- UI presets: any extra per-session values not in _app_settings --------
    # These are settings the frontend stores in DOM state and POSTs back via
    # separate endpoints.  We reconstruct them from _app_settings so they
    # round-trip correctly on import.
    bundle['ui_presets'] = {
        # AI tab voice selection
        'ai_tx_engine':  _app_settings.get('ai_tx_engine', 'espeak'),
        'ai_tx_voice':   _app_settings.get('ai_tx_voice', ''),
        'ai_auto_tx':    _app_settings.get('ai_auto_tx', False),
        # Acid Trip agent A
        'trip_a_name':     _app_settings.get('trip_a_name', 'Alex'),
        'trip_a_emoji':    _app_settings.get('trip_a_emoji', '\U0001f47d'),
        'trip_a_engine':   _app_settings.get('trip_a_engine', 'espeak'),
        'trip_a_voice':    _app_settings.get('trip_a_voice', ''),
        'trip_a_provider': _app_settings.get('trip_a_provider', 'ollama'),
        'trip_a_model':    _app_settings.get('trip_a_model', ''),
        # Acid Trip agent B
        'trip_b_name':     _app_settings.get('trip_b_name', 'Art'),
        'trip_b_emoji':    _app_settings.get('trip_b_emoji', '\U0001f335'),
        'trip_b_engine':   _app_settings.get('trip_b_engine', 'espeak'),
        'trip_b_voice':    _app_settings.get('trip_b_voice', ''),
        'trip_b_provider': _app_settings.get('trip_b_provider', 'ollama'),
        'trip_b_model':    _app_settings.get('trip_b_model', ''),
        # Acid Trip session defaults
        'trip_turns':      _app_settings.get('trip_turns', 6),
        'trip_delay':      _app_settings.get('trip_delay', 1),
        'trip_max_tok':    _app_settings.get('trip_max_tok', 120),
        'trip_temp':       _app_settings.get('trip_temp', 1.1),
        # Transmit tab defaults
        'tx_engine':       _app_settings.get('tx_engine', 'espeak'),
        'tx_voice':        _app_settings.get('tx_voice', ''),
        'tx_delay':        _app_settings.get('tx_delay', 0),
        'tx_repeat':       _app_settings.get('tx_repeat', 1),
    }

    n_b  = len(bundle['beacons'])
    n_sc = len(bundle['schedules'])
    log_event('INFO', 'CONFIG',
              f'Config exported (include_keys={include_keys}, beacons={n_b}, schedules={n_sc})')

    import json as _jsn
    from flask import Response as _FR
    body = _jsn.dumps(bundle, ensure_ascii=True, indent=2)
    ts   = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    return _FR(
        body,
        status=200,
        mimetype='application/json; charset=utf-8',
        headers={'Content-Disposition': f'attachment; filename="riggpt-config-{ts}.json"'}
    )


@app.route('/api/config/export/full', methods=['GET'])
def api_config_export_full():
    """Convenience alias: /api/config/export?include_keys=true."""
    from flask import redirect
    return redirect('/api/config/export?include_keys=true', code=307)


@app.route('/api/config/import', methods=['POST'])
def api_config_import():
    """Import a configuration bundle produced by /api/config/export.

    Restores:
      - All _app_settings keys (gong_path, AI config, serial port, etc.)
      - API keys for every known provider (skips masked ****xxxx values)
      - ui_presets (AI TX voice, Acid Trip agents, Transmit defaults)
      - beacons  (adds any that don't already exist by name)
      - schedules (adds any that don't already exist by message+cron)

    Returns JSON: { success, results, message }
    """
    global _app_settings
    data = request.json or {}
    if data.get('__format__') not in ('riggpt-config', 'ic7610-voice-agent-config'):
        return jsonify({'success': False,
                        'message': 'Invalid config format - expected riggpt-config'}), 400

    results = {
        'settings_applied':  [],
        'api_keys_applied':  [],
        'ui_presets_applied':[],
        'beacons_added':     [],
        'schedules_added':   [],
        'skipped':           [],
        'warnings':          [],
    }

    # -- 1. Core settings -------------------------------------
    # Every key that _app_settings can hold is allowed - we use the
    # same whitelist as /api/settings plus the extra keys added in v2.11.x
    SETTINGS_ALLOWED = {
        # Radio connection
        'serial_port', 'baud_rate', 'ci_v_address',
        # Audio
        'gong_path',
        # AI / Ollama
        'ollama_url', 'ollama_model', 'ollama_enabled',
        'ai_persona', 'ai_temp', 'ai_max_tokens', 'ai_mode',
        # AI TX voice (saved from AI tab)
        'ai_tx_engine', 'ai_tx_voice', 'ai_auto_tx',
        # Acid Trip agents
        'trip_a_name', 'trip_a_emoji', 'trip_a_engine', 'trip_a_voice',
        'trip_a_provider', 'trip_a_model',
        'trip_b_name', 'trip_b_emoji', 'trip_b_engine', 'trip_b_voice',
        'trip_b_provider', 'trip_b_model',
        'trip_turns', 'trip_delay', 'trip_max_tok', 'trip_temp',
        # Transmit tab defaults
        'tx_engine', 'tx_voice', 'tx_delay', 'tx_repeat',
        # Memory / Qdrant
        'memory_enabled', 'memory_qdrant_host', 'memory_embed_model',
    }
    settings_patch = data.get('settings', {})
    for k, v in settings_patch.items():
        if k in SETTINGS_ALLOWED:
            _app_settings[k] = v
            results['settings_applied'].append(k)
        elif not k.startswith('__'):
            results['skipped'].append(f'settings.{k} (unknown key)')

    # -- 2. ui_presets ----------------------------------------
    ui_patch = data.get('ui_presets', {})
    for k, v in ui_patch.items():
        if k in SETTINGS_ALLOWED:
            _app_settings[k] = v
            results['ui_presets_applied'].append(k)

    if results['settings_applied'] or results['ui_presets_applied']:
        _save_app_settings(_app_settings)

    # -- 3. API keys ------------------------------------------
    if _api_keys_ok:
        api_keys_data = data.get('api_keys', {})
        for pid, fields in api_keys_data.items():
            if pid not in _api_keys.PROVIDER_REGISTRY:
                results['skipped'].append(f'api_keys.{pid} (unknown provider)')
                continue
            for field_id, val in fields.items():
                if not val or str(val).startswith('****'):
                    results['skipped'].append(f'{pid}.{field_id} (masked - re-enter manually)')
                    continue
                try:
                    _api_keys.set_key(pid, field_id, str(val))
                    results['api_keys_applied'].append(f'{pid}.{field_id}')
                except Exception as e:
                    results['warnings'].append(f'{pid}.{field_id} write error: {e}')
    else:
        if data.get('api_keys'):
            results['warnings'].append('api_keys module not available - keys not restored')

    # -- 4. Beacons -------------------------------------------
    beacons_in = data.get('beacons', [])
    if beacons_in:
        try:
            existing_resp = api_beacon_list()
            existing = {b['name'] for b in (existing_resp.get_json() or {}).get('beacons', [])}
            for bcn in beacons_in:
                name = bcn.get('name', '').strip()
                if not name or name in existing:
                    results['skipped'].append(f'beacon:{name or "(unnamed)"} (already exists)')
                    continue
                try:
                    with app.test_request_context(
                        '/api/beacons',
                        method='POST',
                        json=bcn,
                        content_type='application/json'
                    ):
                        resp = api_beacon_create()
                        rj   = resp.get_json() if hasattr(resp, 'get_json') else {}
                        if rj.get('success'):
                            results['beacons_added'].append(name)
                            existing.add(name)
                        else:
                            results['warnings'].append(f'beacon:{name} add failed: {rj.get("message")}')
                except Exception as e:
                    results['warnings'].append(f'beacon:{name} error: {e}')
        except Exception as e:
            results['warnings'].append(f'beacon restore error: {e}')

    # -- 5. Schedules -----------------------------------------
    schedules_in = data.get('schedules', [])
    if schedules_in:
        try:
            existing_resp = api_schedule_list()
            existing_jobs = (existing_resp.get_json() or {}).get('jobs', [])
            existing_sigs = {(j.get('message',''), j.get('cron_expression','')) for j in existing_jobs}
            for job in schedules_in:
                sig = (job.get('message', ''), job.get('cron_expression', ''))
                if sig in existing_sigs:
                    results['skipped'].append(f'schedule:{sig[1]} "{sig[0][:30]}" (already exists)')
                    continue
                try:
                    with app.test_request_context(
                        '/api/schedules',
                        method='POST',
                        json=job,
                        content_type='application/json'
                    ):
                        resp = api_schedule_add()
                        rj   = resp.get_json() if hasattr(resp, 'get_json') else {}
                        if rj.get('success'):
                            results['schedules_added'].append(f'{sig[1]} "{sig[0][:30]}"')
                            existing_sigs.add(sig)
                        else:
                            results['warnings'].append(f'schedule add failed: {rj.get("message")}')
                except Exception as e:
                    results['warnings'].append(f'schedule add error: {e}')
        except Exception as e:
            results['warnings'].append(f'schedule restore error: {e}')

    log_event('INFO', 'CONFIG', f'Config imported: {results}')

    ns = len(results["settings_applied"])
    nk = len(results["api_keys_applied"])
    nu = len(results["ui_presets_applied"])
    nb = len(results["beacons_added"])
    nj = len(results["schedules_added"])
    nw = len(results["warnings"])
    msg = (f'Imported {ns} settings, {nk} API key fields, {nu} UI presets, '
           f'{nb} beacons, {nj} schedules'
           + (f' ({nw} warnings)' if nw else ''))

    return jsonify({'success': True, 'results': results, 'message': msg})


# -------------------------------------------------------------
# AI Integration Framework  (v2.11.3)
# Local LLM integration via Ollama + debug logging + preview
# -------------------------------------------------------------

# -- Ollama URL normaliser -------------------------------------
def _ollama_url() -> str:
    """Return the configured Ollama base URL, always with an http:// scheme."""
    raw = _app_settings.get('ollama_url', 'http://192.168.40.15:11434').strip().rstrip('/')
    if raw and '://' not in raw:
        raw = 'http://' + raw   # user forgot the scheme - add it automatically
    return raw

# -- AI debug ring buffer --------------------------------------
import collections as _collections
_AI_DEBUG_MAX  = 400          # max lines kept in memory
_ai_debug_log  = _collections.deque(maxlen=_AI_DEBUG_MAX)
_ai_debug_on   = False        # toggled via /api/ai/debug/toggle

def _ailog(level: str, msg: str):
    """Append a timestamped entry to the AI debug ring buffer and to journald."""
    ts   = datetime.now(timezone.utc).strftime('%H:%M:%S.%f')[:-3]
    line = f"[{ts}] [{level}] {msg}"
    _ai_debug_log.append(line)
    if level == 'ERROR':
        logger.error(f'AI: {msg}')
    elif _ai_debug_on or level in ('WARN', 'ERROR'):
        logger.info(f'AI: {msg}')
    else:
        logger.debug(f'AI: {msg}')

@app.route('/api/ai/debug/log', methods=['GET'])
def api_ai_debug_log():
    """Return the AI debug ring buffer as a list of strings."""
    n    = request.args.get('n', 200, type=int)
    tail = list(_ai_debug_log)[-n:]
    return jsonify({'lines': tail, 'verbose': _ai_debug_on, 'total': len(_ai_debug_log)})

@app.route('/api/ai/debug/toggle', methods=['POST'])
def api_ai_debug_toggle():
    """Toggle verbose AI debug logging."""
    global _ai_debug_on
    _ai_debug_on = not _ai_debug_on
    _ailog('INFO', f'Verbose AI logging {"ENABLED" if _ai_debug_on else "DISABLED"}')
    return jsonify({'success': True, 'verbose': _ai_debug_on})

@app.route('/api/ai/debug/clear', methods=['POST'])
def api_ai_debug_clear():
    """Clear the AI debug ring buffer."""
    _ai_debug_log.clear()
    return jsonify({'success': True})

# -- Config ---------------------------------------------------
@app.route('/api/ai/config', methods=['GET'])
def api_ai_config_get():
    """Return AI integration configuration."""
    cfg = {
        'ollama_url':     _app_settings.get('ollama_url',  'http://192.168.40.15:11434'),
        'ollama_model':   _app_settings.get('ollama_model','llama3'),
        'ollama_enabled': _app_settings.get('ollama_enabled', False),
        'ai_persona':     _app_settings.get('ai_persona',  'You are a ham radio operator assistant.'),
        'ai_temp':        float(_app_settings.get('ai_temp', 0.8)),
        'ai_max_tokens':  int(_app_settings.get('ai_max_tokens', 200)),
        'ai_mode':        _app_settings.get('ai_mode', 'manual'),
    }
    _ailog('DEBUG', f'Config read: url={cfg["ollama_url"]} model={cfg["ollama_model"]}')
    return jsonify(cfg)

@app.route('/api/ai/config', methods=['POST'])
def api_ai_config_post():
    """Save AI integration configuration."""
    global _app_settings
    data    = request.json or {}
    allowed = {'ollama_url','ollama_model','ollama_enabled','ai_persona',
               'ai_temp','ai_max_tokens','ai_mode'}
    changed = {}
    for k, v in data.items():
        if k in allowed:
            _app_settings[k] = v
            changed[k] = v
    _save_app_settings(_app_settings)
    _ailog('INFO', f'Config saved: {changed}')
    return jsonify({'success': True})

# -- Model discovery ------------------------------------------
def _ascii(s) -> str:
    """Sanitize to pure ASCII so Flask latin-1 encoder never chokes on
    Unicode in external API error bodies (Gemini bullets, smart quotes, etc.)."""
    if not s:
        return ''
    return str(s).encode('ascii', errors='replace').decode('ascii')


@app.route('/api/ai/models', methods=['GET'])
def api_ai_models():
    """Probe Ollama for available local models."""
    url = _ollama_url()
    _ailog('INFO', f'Probing Ollama at {url}/api/tags')
    try:
        r = requests.get(f'{url}/api/tags', timeout=5)
        _ailog('DEBUG', f'Ollama /api/tags - HTTP {r.status_code}')
        if r.status_code == 200:
            models = [m['name'] for m in r.json().get('models', [])]
            _ailog('INFO', f'Models found: {models}')
            return jsonify({'success': True, 'models': models, 'ollama_url': url})
        _ailog('ERROR', f'Ollama returned HTTP {r.status_code}: {r.text[:120]}')
        return jsonify({'success': False, 'message': f'Ollama returned HTTP {r.status_code}'}), 502
    except Exception as e:
        _ailog('ERROR', f'Cannot reach Ollama at {url}: {e}')
        return jsonify({'success': False, 'message': _ascii(f'Cannot reach Ollama at {url}: {e}')}), 503


@app.route('/api/ai/models-all', methods=['GET'])
def api_ai_models_all():
    """
    Return all available LLM models across providers:
      - Ollama (local): always probed
      - OpenAI: if openai_chat API key is configured
      - Gemini: if gemini API key is configured
    Response: {
      providers: {
        ollama:  { available: bool, models: [str], error?: str },
        openai:  { available: bool, key_configured: bool, models: [str] },
        gemini:  { available: bool, key_configured: bool, models: [str] },
      }
    }
    """
    result = {}

    # -- Ollama ----------------------------------------------
    url = _ollama_url()
    try:
        r = requests.get(f'{url}/api/tags', timeout=5)
        if r.status_code == 200:
            ollama_models = [m['name'] for m in r.json().get('models', [])]
            result['ollama'] = {'available': True, 'models': ollama_models}
        else:
            result['ollama'] = {'available': False, 'models': [], 'error': f'HTTP {r.status_code}'}
    except Exception as e:
        result['ollama'] = {'available': False, 'models': [], 'error': str(e)}

    # -- OpenAI ----------------------------------------------
    openai_key = ''
    if _api_keys_ok:
        openai_key = _api_keys.get_key('openai_chat', 'api_key') or _api_keys.get_key('openai', 'api_key') or ''
    if not openai_key:
        import os
        openai_key = os.environ.get('OPENAI_API_KEY', '')

    if openai_key:
        result['openai'] = {
            'available': True,
            'key_configured': True,
            'models': ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'],
        }
    else:
        result['openai'] = {'available': False, 'key_configured': False, 'models': []}

    # -- Gemini ----------------------------------------------
    gemini_key = ''
    if _api_keys_ok:
        gemini_key = _api_keys.get_key('gemini', 'api_key') or ''
    if not gemini_key:
        import os
        gemini_key = os.environ.get('GEMINI_API_KEY', '')

    if gemini_key:
        # Probe the API for the real live model list rather than using a
        # hardcoded list that goes stale when Google deprecates models.
        _gemini_fallback = ['gemini-2.0-flash', 'gemini-2.0-flash-lite',
                            'gemini-1.5-flash-8b']
        try:
            _gr = requests.get(
                'https://generativelanguage.googleapis.com/v1beta/models',
                params={'key': gemini_key},
                timeout=6
            )
            if _gr.status_code == 200:
                _all = _gr.json().get('models', [])
                _gen = [
                    m.get('name', '').split('/')[-1]
                    for m in _all
                    if 'generateContent' in m.get('supportedGenerationMethods', [])
                    and 'gemini' in m.get('name', '').lower()
                    and 'embedding' not in m.get('name', '').lower()
                ]
                _gemini_models = sorted(_gen) if _gen else _gemini_fallback
            else:
                _gemini_models = _gemini_fallback
        except Exception:
            _gemini_models = _gemini_fallback
        result['gemini'] = {
            'available': True,
            'key_configured': True,
            'models': _gemini_models,
        }
    else:
        result['gemini'] = {'available': False, 'key_configured': False, 'models': []}

    return jsonify({'success': True, 'providers': result})

# -- Single-shot generation -----------------------------------
@app.route('/api/ai/generate', methods=['POST'])
def api_ai_generate():
    """
    Generate text via Ollama /api/generate (single-turn, no history).
    Used by the INSPIRE button.  Does NOT transmit - returns text only.
    POST: { prompt, system?, model?, temperature?, max_tokens? }
    """
    data   = request.json or {}
    url    = _ollama_url()
    model  = data.get('model') or _app_settings.get('ollama_model', 'llama3')
    system = data.get('system') or _app_settings.get('ai_persona', 'You are a ham radio operator.')
    prompt = data.get('prompt', '').strip()
    temp   = float(data.get('temperature', _app_settings.get('ai_temp', 0.8)))
    maxT   = int(data.get('max_tokens', min(int(_app_settings.get('ai_max_tokens', 200)), 120)))

    _ailog('INFO', f'generate() model={model} temp={temp} maxT={maxT} prompt={prompt[:80]!r}')
    if not prompt:
        return jsonify({'success': False, 'message': 'prompt is required'}), 400

    try:
        payload = {
            'model':   model,
            'prompt':  prompt,
            'system':  system,
            'stream':  False,
            'options': {'temperature': temp, 'num_predict': maxT},
        }
        _ailog('DEBUG', f'POST {url}/api/generate payload_keys={list(payload.keys())}')
        r = requests.post(f'{url}/api/generate', json=payload, timeout=60)
        _ailog('DEBUG', f'Ollama /api/generate - HTTP {r.status_code}')
        if r.status_code != 200:
            _ailog('ERROR', f'Ollama error HTTP {r.status_code}: {r.text[:200]}')
            return jsonify({'success': False, 'message': f'Ollama error: HTTP {r.status_code}'}), 502
        generated = r.json().get('response', '').strip()
        _ailog('INFO', f'generate() got {len(generated)} chars: {generated[:80]!r}')
        log_event('INFO', 'AI', f'Generated {len(generated)} chars via {model}')
        return jsonify({'success': True, 'generated': generated, 'model': model})
    except Exception as e:
        _ailog('ERROR', f'generate() exception: {e}')
        return jsonify({'success': False, 'message': str(e)}), 503

# -- Multi-turn chat + optional TX ----------------------------
def _sanitise_trip_reply(text: str) -> str:
    """
    Strip any system-prompt scaffolding that leaked into the model's reply.
    This is a safety net for weak models that echo their instructions.
    Applied to all /api/ai/chat replies when called from the Acid Trip loop.
    """
    import re as _re

    # Remove lines that look like system-prompt headers or metadata
    # e.g. "BACKGROUND:", "Topic:", "Opponent:", "CRITICAL OUTPUT RULE:", "[CRITICAL:", "[Background:"
    BAD_PREFIXES = (
        'BACKGROUND:', 'Topic:', 'Opponent:', 'The debate topic',
        'CRITICAL OUTPUT RULE:', '[CRITICAL', '[Background', '[IMPORTANT',
        'Discord', 'Reply in ', 'Stay in character', 'Deliver your response',
    )
    lines = text.splitlines()
    clean = []
    for line in lines:
        stripped = line.strip()
        # Drop blank lines only if we have nothing yet (leading whitespace)
        if not stripped:
            if clean:
                clean.append('')
            continue
        if any(stripped.startswith(p) for p in BAD_PREFIXES):
            continue
        clean.append(line)

    text = '\n'.join(clean).strip()

    # Remove any remaining bracketed metadata blocks: [CRITICAL: ...] [Background: ...]
    text = _re.sub(r'\[(?:CRITICAL|IMPORTANT|Background|Discord)[^\]]{0,400}\]', '', text, flags=_re.DOTALL)

    # Remove leading labels like "Agent A:" or "Alex:" that aren't part of speech
    # Only strip if it's at the very start and followed by a space
    text = _re.sub(r'^[A-Z][A-Za-z\s]{0,20}:\s*', '', text)

    # Strip Discord markup tokens that may have leaked into model output
    # <#channel_id>  <@user_id>  <@&role_id>  <:emoji_name:id>  <a:emoji_name:id>
    text = _re.sub(r'<[#@][^>]{1,40}>', '', text)
    text = _re.sub(r'<a?:[A-Za-z0-9_]{1,32}:\d+>', '', text)
    text = _re.sub(r'  +', ' ', text)  # collapse double spaces left by removed tokens

    # Collapse multiple blank lines to one
    text = _re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def _chat_via_openai(messages, model, temp, maxT, api_key):
    """
    Call OpenAI /v1/chat/completions.
    Returns (reply_str, prompt_tokens, response_tokens) or raises on error.
    messages must already include system role if desired.
    """
    import os as _os
    key = api_key or _os.environ.get('OPENAI_API_KEY', '')
    if not key:
        raise ValueError('OpenAI API key not configured')
    payload = {
        'model':       model,
        'messages':    messages,
        'max_tokens':  int(maxT),
        'temperature': float(temp),
    }
    r = requests.post(
        'https://api.openai.com/v1/chat/completions',
        headers={'Authorization': f'Bearer {key}', 'Content-Type': 'application/json'},
        json=payload,
        timeout=60,
    )
    if r.status_code != 200:
        raise RuntimeError(_ascii(f'OpenAI HTTP {r.status_code}: {r.text[:200]}'))
    rj    = r.json()
    reply = rj['choices'][0]['message']['content'].strip()
    usage = rj.get('usage', {})
    return reply, usage.get('prompt_tokens', 0), usage.get('completion_tokens', 0)


def _chat_via_gemini(messages, model, temp, maxT, api_key):
    """
    Call Google Gemini generateContent.
    Converts OpenAI-style messages list to Gemini format.
    Returns (reply_str, 0, 0) - Gemini token counts not always returned.
    """
    import os as _os
    key = api_key or _os.environ.get('GEMINI_API_KEY', '')
    if not key:
        raise ValueError('Gemini API key not configured')

    # Extract system instruction (first message with role=system if present)
    system_parts = []
    contents = []
    for m in messages:
        role = m.get('role', '')
        text = m.get('content', '')
        if role == 'system':
            system_parts.append({'text': text})
        elif role == 'user':
            contents.append({'role': 'user', 'parts': [{'text': text}]})
        elif role == 'assistant':
            contents.append({'role': 'model', 'parts': [{'text': text}]})

    payload = {
        'contents': contents,
        'generationConfig': {
            'maxOutputTokens': int(maxT),
            'temperature': float(temp),
        },
    }
    if system_parts:
        payload['systemInstruction'] = {'parts': system_parts}

    url = (f'https://generativelanguage.googleapis.com/v1beta/models/'
           f'{model}:generateContent?key={key}')
    r = requests.post(url, json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(_ascii(f'Gemini HTTP {r.status_code}: {r.text[:200]}'))
    rj = r.json()
    try:
        reply = rj['candidates'][0]['content']['parts'][0]['text'].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f'Unexpected Gemini response structure: {rj}') from e
    usage = rj.get('usageMetadata', {})
    return reply, usage.get('promptTokenCount', 0), usage.get('candidatesTokenCount', 0)


@app.route('/api/ai/chat', methods=['POST'])
def api_ai_chat():
    """
    Multi-turn chat with Ollama/OpenAI/Gemini + optional transmission.
    Provider is determined by the model field:
      - 'openai:<model>'  - OpenAI ChatCompletions (e.g. 'openai:gpt-4o-mini')
      - 'gemini:<model>'  - Google Gemini (e.g. 'gemini:gemini-1.5-flash')
      - anything else     - Ollama (local)
    TX runs in a daemon thread so HTTP returns quickly with tx_queued:true.
    POST: { messages, model?, temperature?, max_tokens?, transmit?, engine?, voice? }
    """
    data     = request.json or {}
    raw_model = data.get('model') or _app_settings.get('ollama_model', 'llama3')
    messages = data.get('messages', [])
    temp     = float(data.get('temperature', _app_settings.get('ai_temp', 0.8)))
    maxT     = int(data.get('max_tokens',    _app_settings.get('ai_max_tokens', 200)))
    do_tx    = bool(data.get('transmit', False))
    engine   = data.get('engine', 'espeak') or 'espeak'
    voice    = data.get('voice') or None

    # Parse provider prefix: 'openai:gpt-4o' - provider='openai', model='gpt-4o'
    if ':' in raw_model and raw_model.split(':')[0] in ('openai', 'gemini'):
        provider, model = raw_model.split(':', 1)
    else:
        provider, model = 'ollama', raw_model

    _ailog('INFO',
        f'chat() provider={provider} model={model} msgs={len(messages)} temp={temp} maxT={maxT} '
        f'transmit={do_tx} engine={engine} voice={voice!r}')

    if not messages:
        return jsonify({'success': False, 'message': 'messages list is required'}), 400

    # Inject system persona: caller can override via 'system' field in POST body
    persona = data.get('system') or _app_settings.get('ai_persona', 'You are a ham radio operator.')

    # Memory augmentation: append Discord community context to the system prompt
    # Only fires when memory_enabled='true' and Qdrant is reachable.
    # trip_turn=0 + trip_briefing=true - full pre-trip briefing for both agents.
    if _app_settings.get('memory_enabled', 'false') == 'true':
        try:
            mem      = _get_memory()
            topic    = data.get('trip_topic', '') or ''
            turn     = int(data.get('trip_turn', 0) or 0)
            agent    = data.get('trip_agent', 'a') or 'a'
            briefing = bool(data.get('trip_briefing', False))
            if briefing and turn == 0 and topic:
                # Pre-trip briefing: richer one-time context at trip start
                mem_ctx = mem.build_briefing(topic)
                _ailog('DEBUG', f'Memory briefing injected ({len(mem_ctx)} chars)')
            else:
                mem_ctx = mem.build_context(topic or persona[:120], turn, agent)
                _ailog('DEBUG', f'Memory context injected ({len(mem_ctx)} chars)')
            if mem_ctx:
                persona = persona + '\n\n' + mem_ctx
        except Exception as _mem_exc:
            _ailog('WARN', f'Memory inject failed: {_ascii(str(_mem_exc))}')

    if messages[0].get('role') != 'system':
        messages = [{'role': 'system', 'content': persona}] + messages
        _ailog('DEBUG', f'Prepended system persona ({len(persona)} chars): {persona[:60]!r}')

    try:
        if provider == 'openai':
            openai_key = ''
            if _api_keys_ok:
                openai_key = _api_keys.get_key('openai_chat', 'api_key') or _api_keys.get_key('openai', 'api_key') or ''
            _ailog('INFO', f'Routing to OpenAI model={model!r}')
            reply, ptoks, rtoks = _chat_via_openai(messages, model, temp, maxT, openai_key)

        elif provider == 'gemini':
            gemini_key = ''
            if _api_keys_ok:
                gemini_key = _api_keys.get_key('gemini', 'api_key') or ''
            _ailog('INFO', f'Routing to Gemini model={model!r}')
            reply, ptoks, rtoks = _chat_via_gemini(messages, model, temp, maxT, gemini_key)

        else:
            # -- Ollama path (original) ------------------------------
            url = _ollama_url()
            # num_ctx: ensure context window fits system prompt + history + output
            # num_predict: floor at 300 - thinking models (qwen3 etc) use tokens for CoT before output
            # think: false - disable chain-of-thought on models that support it (Ollama >= 0.6.0)
            payload = {
                'model':    model,
                'messages': messages,
                'stream':   False,
                'think':    False,   # qwen3/deepseek-r1: suppress <think> block, return only response
                'options':  {
                    'temperature': temp,
                    'num_predict': int(maxT),
                    'num_ctx':     4096,
                },
            }
            _ailog('DEBUG', f'POST {url}/api/chat model={model!r} msgs={len(messages)} num_predict={max(int(maxT),150)} num_ctx=4096')
            r = requests.post(f'{url}/api/chat', json=payload, timeout=90)
            _ailog('DEBUG', f'Ollama /api/chat - HTTP {r.status_code}')

            if r.status_code != 200:
                _ollama_body = r.text[:300]
                _ailog('ERROR', f'Ollama /api/chat HTTP {r.status_code}: {_ollama_body}')
                try:
                    _err_msg = r.json().get('error', _ollama_body)
                except Exception:
                    _err_msg = _ollama_body
                return jsonify({'success': False, 'message': f'Ollama HTTP {r.status_code}: {_err_msg}'}), 502

            rj    = r.json()
            msg   = rj.get('message', {})
            # qwen3 and other thinking models put CoT in 'thinking' field, leaving 'content' empty.
            reply = msg.get('content', '').strip()
            if not reply:
                thinking = msg.get('thinking', '').strip()
                if thinking:
                    _ailog('WARN', f'content empty, using thinking field ({len(thinking)} chars) - model may be a CoT thinker')
                    reply = thinking
            ptoks = rj.get('prompt_eval_count', 0)
            rtoks = rj.get('eval_count', 0)

        # Sanitise: strip any leaked system-prompt scaffolding before TTS/return
        reply = _sanitise_trip_reply(reply)
        _ailog('INFO', f'chat() reply {len(reply)} chars prompt_tok={ptoks} resp_tok={rtoks}: {reply[:80]!r}')
        log_event('INFO', 'AI', f'Chat reply {len(reply)} chars via {provider}:{model}')

        if not reply:
            if provider == 'ollama':
                rj_done = rj.get('done_reason') or rj.get('done', '')
                _ailog('WARN', f'Empty reply: done={rj_done!r} ptoks={ptoks} rtoks={rtoks} model={model!r}')
                return jsonify({'success': False,
                    'message': (
                        f'Ollama empty response: done_reason={rj_done!r} '
                        f'prompt_tokens={ptoks} reply_tokens={rtoks} model={model!r}. '
                        f'If done=length: increase MAX TOK or shorten system prompt. '
                        f'Run - TEST LLM in trip debug panel to diagnose.'
                    )}), 502
            return jsonify({'success': False, 'message': f'{provider} returned empty response'}), 502

        if do_tx:
            # Run TX in a background thread so HTTP returns immediately.
            # The result is logged to the AI debug buffer and transmission log.
            def _do_tx():
                _ailog('INFO', f'TX thread starting: engine={engine} voice={voice!r} text={reply[:60]!r}')
                try:
                    result = orchestrator.execute(reply, engine=engine, voice=voice or None)
                    if result.get('success'):
                        _ailog('INFO', f'TX complete: duration={result.get("duration","?")}s')
                    else:
                        _ailog('ERROR', f'TX failed: {result.get("message","unknown error")}')
                except Exception as tex:
                    _ailog('ERROR', f'TX thread exception: {tex}')
            t = threading.Thread(target=_do_tx, daemon=True, name='ai-tx')
            t.start()
            _ailog('INFO', 'TX thread launched, returning to client')
            return jsonify({
                'success':   True,
                'reply':     reply,
                'model':     model,
                'tx_queued': True,
                'prompt_tokens':   ptoks,
                'response_tokens': rtoks,
            })

        return jsonify({
            'success':         True,
            'reply':           reply,
            'model':           model,
            'tx_queued':       False,
            'prompt_tokens':   ptoks,
            'response_tokens': rtoks,
        })

    except Exception as e:
        _ailog('ERROR', f'chat() exception: {e}')
        return jsonify({'success': False, 'message': _ascii(str(e))}), 503

# -- Preview: generate text + synthesize locally (no PTT) -----
@app.route('/api/ai/preview', methods=['POST'])
def api_ai_preview():
    """
    Generate text from a prompt and synthesize it locally to WAV.
    Returns base64-encoded WAV for browser playback - no PTT, no transmission.
    POST: { prompt, system?, model?, temperature?, max_tokens?, engine?, voice? }
    """
    import base64
    data   = request.json or {}
    url    = _ollama_url()
    model  = data.get('model') or _app_settings.get('ollama_model', 'llama3')
    system = data.get('system') or _app_settings.get('ai_persona', 'You are a ham radio operator.')
    prompt = data.get('prompt', '').strip()
    engine = data.get('engine', 'espeak') or 'espeak'
    voice  = data.get('voice') or None
    temp   = float(data.get('temperature', _app_settings.get('ai_temp', 0.8)))
    maxT   = int(data.get('max_tokens', min(int(_app_settings.get('ai_max_tokens', 200)), 150)))

    _ailog('INFO', f'preview() model={model} engine={engine} prompt={prompt[:60]!r}')
    if not prompt:
        return jsonify({'success': False, 'message': 'prompt required'}), 400

    # 1. Generate text
    try:
        r = requests.post(f'{url}/api/generate', json={
            'model': model, 'prompt': prompt, 'system': system,
            'stream': False, 'options': {'temperature': temp, 'num_predict': maxT},
        }, timeout=60)
        if r.status_code != 200:
            _ailog('ERROR', f'preview() Ollama error HTTP {r.status_code}')
            return jsonify({'success': False, 'message': f'Ollama error HTTP {r.status_code}'}), 502
        text = r.json().get('response', '').strip()
        _ailog('INFO', f'preview() generated {len(text)} chars')
    except Exception as e:
        _ailog('ERROR', f'preview() generate exception: {e}')
        return jsonify({'success': False, 'message': f'Ollama error: {e}'}), 503

    if not text:
        return jsonify({'success': False, 'message': 'Ollama returned empty response'}), 502

    # 2. Synthesize to WAV
    _ailog('INFO', f'preview() synthesizing via {engine}')
    try:
        if engine == 'espeak':
            wav = orchestrator.espeak_agent.synthesize(text)
        elif engine == 'edge':
            wav = orchestrator.edge_agent.synthesize(text, voice=voice)
        elif engine == 'gtts':
            wav = orchestrator.gtts_agent.synthesize(text, voice=voice)
        else:
            wav = orchestrator.piper_agent.synthesize(text, voice=voice)
        if not wav or not os.path.exists(wav):
            _ailog('ERROR', 'preview() synthesis returned no file')
            return jsonify({'success': False, 'message': 'TTS synthesis failed'}), 500
        with open(wav, 'rb') as f:
            wav_b64 = base64.b64encode(f.read()).decode('ascii')
        try:
            os.remove(wav)
        except Exception:
            pass
        _ailog('INFO', f'preview() synthesized {len(wav_b64)} b64 chars, returning')
        return jsonify({'success': True, 'text': text, 'wav_b64': wav_b64, 'model': model})
    except Exception as e:
        _ailog('ERROR', f'preview() synthesis exception: {e}')
        return jsonify({'success': False, 'message': f'Synthesis error: {e}'}), 500

# -- AI diagnostic endpoint ----------------------------------
@app.route('/api/ai/test', methods=['POST'])
def api_ai_test():
    """
    Send a minimal message to Ollama and return the full raw response for diagnostics.
    POST: { model?, message? }
    """
    data  = request.json or {}
    url   = _ollama_url()
    model = data.get('model') or _app_settings.get('ollama_model', 'llama3')
    msg   = data.get('message', 'Say exactly: TEST OK')
    max_t = int(data.get('max_tokens', 50))

    _ailog('INFO', f'test() model={model!r} url={url} max_tokens={max_t}')
    try:
        payload = {
            'model':   model,
            'messages': [
                {'role': 'system', 'content': 'You are a test assistant. Follow instructions exactly.'},
                {'role': 'user',   'content': msg},
            ],
            'stream':  False,
            'options': {'temperature': 0.1, 'num_predict': max_t, 'num_ctx': 4096},
        }
        r = requests.post(f'{url}/api/chat', json=payload, timeout=30)
        _ailog('INFO', f'test() Ollama HTTP {r.status_code}')
        raw = r.json() if r.headers.get('content-type','').startswith('application/json') else {'raw_text': r.text[:500]}
        content = raw.get('message', {}).get('content', '') if isinstance(raw, dict) else ''
        done    = raw.get('done_reason', '?') if isinstance(raw, dict) else '?'
        ptoks   = raw.get('prompt_eval_count', '?') if isinstance(raw, dict) else '?'
        rtoks   = raw.get('eval_count', '?') if isinstance(raw, dict) else '?'
        _ailog('INFO', f'test() done={done!r} ptoks={ptoks} rtoks={rtoks} content={content!r}')
        return jsonify({
            'success':      r.status_code == 200 and bool(content),
            'http_status':  r.status_code,
            'model':        model,
            'content':      content,
            'done_reason':  done,
            'prompt_tokens': ptoks,
            'reply_tokens':  rtoks,
            'full_response': raw,
        })
    except Exception as e:
        _ailog('ERROR', f'test() exception: {e}')
        return jsonify({'success': False, 'message': str(e), 'model': model}), 503

# -- Example prompts catalogue --------------------------------
@app.route('/api/ai/examples', methods=['GET'])
def api_ai_examples():
    """Return pre-canned example prompts for the AI tab."""
    examples = [
        {'id': 'cq_call',    'label': 'CQ CALL',    'category': 'on-air',
         'prompt': 'Write a short CQ call for 20 meter SSB. Include the callsign W1AW. Keep it under 20 words.'},
        {'id': 'signal_rpt', 'label': 'SIG REPORT', 'category': 'on-air',
         'prompt': 'Give a friendly signal report. Signal is 59. Mention good copy and light QSB. Under 25 words.'},
        {'id': 'contest_ex', 'label': 'CONTEST',    'category': 'on-air',
         'prompt': 'Generate a concise contest exchange: RST 59, serial number 042, state Maine. Ham radio style.'},
        {'id': 'weather',    'label': 'WEATHER RPT', 'category': 'on-air',
         'prompt': 'Give a brief weather report for the ham shack: clear skies, temperature 68F, low humidity. Casual radio style, under 20 words.'},
        {'id': 'sign_off',   'label': 'SIGN OFF',   'category': 'on-air',
         'prompt': 'Write a friendly ham radio sign-off. Use 73 and include W1AW. Under 15 words.'},
        {'id': 'weird',      'label': 'WEIRD TX',   'category': 'experimental',
         'prompt': 'Generate a surreal, abstract radio transmission. Strange imagery, cryptic, poetic. Max 2 sentences.'},
        {'id': 'numbers',    'label': 'NUMBERS STN', 'category': 'experimental',
         'prompt': 'Generate a numbers-station-style message. Use random groups of 5 digits, phonetic letters, and eerie phrasing. 3 groups.'},
        {'id': 'poem',       'label': 'RF POEM',    'category': 'experimental',
         'prompt': 'Write a very short poem about radio waves, static, and the ionosphere. 2-3 lines.'},
        {'id': 'propaganda', 'label': 'PROPAGANDA', 'category': 'experimental',
         'prompt': 'Write a retro-style Cold War propaganda broadcast in the style of shortwave radio. Dramatic, ominous, cryptic. 2 sentences.'},
        {'id': 'technobabel','label': 'TECHNOBABEL', 'category': 'experimental',
         'prompt': 'Invent fake technical jargon as if explaining a nonexistent radio protocol. Sound confident and deeply technical. 2 sentences.'},
        {'id': 'sstv_ann',   'label': 'SSTV ANNOUNCE','category': 'utility',
         'prompt': 'Announce an upcoming SSTV transmission on 14.230 MHz. Mode is Robot36. Casual, informative, under 20 words.'},
        {'id': 'beacon_id',  'label': 'BEACON ID',  'category': 'utility',
         'prompt': 'Write a beacon station identification. Callsign W1AW/B, 10 meters, continuous operation. Formal, brief.'},
        {'id': 'net_open',   'label': 'NET OPEN',   'category': 'utility',
         'prompt': 'Open a ham radio net on 7.250 MHz LSB. Friendly, organized, request check-ins. Under 30 words.'},
        {'id': 'aprs_voice', 'label': 'APRS VOICE', 'category': 'utility',
         'prompt': 'Announce a position report: grid square FN42, heading north at 35 MPH, altitude 450 feet. Radio style.'},
    ]
    return jsonify({'success': True, 'examples': examples})


# -------------------------------------------------------------
# Global JSON error handlers
# -------------------------------------------------------------
@app.errorhandler(404)
def err_404(e):
    return jsonify({'error': 'Not found', 'path': request.path}), 404

@app.errorhandler(500)
def err_500(e):
    logger.error(f'Unhandled 500: {e}')
    return jsonify({'error': 'Internal server error', 'detail': str(e)}), 500

@app.errorhandler(405)
def err_405(e):
    return jsonify({'error': 'Method not allowed', 'allowed': list(e.valid_methods or [])}), 405

@app.errorhandler(Exception)
def err_any(e):
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return jsonify({'error': e.description, 'code': e.code}), e.code
    import traceback
    logger.error(f'Unhandled exception: {type(e).__name__}: {e}\n{traceback.format_exc()}')
    return jsonify({'error': str(e), 'type': type(e).__name__}), 500


# -------------------------------------------------------------
# Startup
# -------------------------------------------------------------


# =============================================================
# v2.10.15 -- Extended APIs
# =============================================================

# -- History: extended log -------------------------------------
@app.route('/api/log/transmissions')
def api_log():
    limit   = int(request.args.get('limit', 100))
    offset  = int(request.args.get('offset', 0))
    engine  = request.args.get('engine', '')
    success = request.args.get('success', '')
    search  = request.args.get('search', '')
    since   = request.args.get('since', '')
    try:
        conn   = sqlite3.connect(DB_PATH)
        where, params = [], []
        if engine:      where.append('engine=?');           params.append(engine)
        if success!='': where.append('success=?');          params.append(int(success))
        if search:      where.append('message LIKE ?');     params.append(f'%{search}%')
        if since:       where.append("timestamp >= ?");     params.append(since)
        wc = ('WHERE '+' AND '.join(where)) if where else ''
        rows  = conn.execute(
            f'SELECT id,timestamp,message,engine,voice,preset,duration,success,notes,'
            f'COALESCE(frequency,0),COALESCE(mode,\'\'),COALESCE(char_count,0),'
            f'COALESCE(wav_cached,0)'
            f' FROM transmissions {wc} ORDER BY id DESC LIMIT ? OFFSET ?',
            params+[limit, offset]).fetchall()
        total = conn.execute(f'SELECT COUNT(*) FROM transmissions {wc}', params).fetchone()[0]
        conn.close()
        keys = ['id','timestamp','message','engine','voice','preset',
                'duration','success','notes','frequency','mode','char_count','wav_cached']
        return jsonify({'transmissions':[dict(zip(keys,r)) for r in rows],
                        'total':total, 'limit':limit, 'offset':offset})
    except Exception as e:
        return jsonify({'error':str(e),'transmissions':[]}), 500


@app.route('/api/log/stats')
def api_log_stats():
    try:
        conn = sqlite3.connect(DB_PATH)
        total    = conn.execute('SELECT COUNT(*) FROM transmissions').fetchone()[0]
        ok       = conn.execute('SELECT COUNT(*) FROM transmissions WHERE success=1').fetchone()[0]
        avg_dur  = conn.execute('SELECT AVG(duration) FROM transmissions WHERE success=1').fetchone()[0]
        tot_dur  = conn.execute('SELECT SUM(duration) FROM transmissions WHERE success=1').fetchone()[0]
        try:
            tot_chr = conn.execute('SELECT SUM(char_count) FROM transmissions').fetchone()[0]
        except Exception:
            tot_chr = 0
        engines  = conn.execute(
            'SELECT engine,COUNT(*) n FROM transmissions GROUP BY engine ORDER BY n DESC').fetchall()
        daily    = conn.execute(
            "SELECT date(timestamp) d, COUNT(*) n FROM transmissions "
            "WHERE timestamp>=date('now','-30 days') GROUP BY d ORDER BY d").fetchall()
        fails    = conn.execute(
            "SELECT timestamp,message,engine,notes FROM transmissions "
            "WHERE success=0 ORDER BY id DESC LIMIT 10").fetchall()
        conn.close()
        return jsonify({
            'total': total, 'successful': ok, 'failed': total-ok,
            'success_rate': round(ok/total*100,1) if total else 0,
            'avg_duration': round(avg_dur or 0,2),
            'total_air_time': round(tot_dur or 0,1),
            'total_chars': tot_chr or 0,
            'engines': [{'engine':e,'count':n} for e,n in engines],
            'daily_activity': [{'date':d,'count':n} for d,n in daily],
            'recent_failures': [
                {'timestamp':r[0],'message':(r[1] or '')[:60],'engine':r[2],'notes':r[3]}
                for r in fails],
        })
    except Exception as e:
        return jsonify({'error':str(e)}), 500


@app.route('/api/log/delete/<int:tx_id>', methods=['DELETE'])
def api_log_delete(tx_id):
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('DELETE FROM transmissions WHERE id=?', (tx_id,))
        conn.commit(); conn.close()
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}), 500


@app.route('/api/log/clear', methods=['DELETE'])
def api_log_clear():
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute('DELETE FROM transmissions')
        conn.commit(); conn.close()
        log_event('WARN','LOG','Transmission log cleared by user')
        return jsonify({'success':True})
    except Exception as e:
        return jsonify({'success':False,'error':str(e)}), 500


@app.route('/api/log/export')
def api_log_export():
    import csv, io
    try:
        conn = sqlite3.connect(DB_PATH)
        rows = conn.execute(
            'SELECT id,timestamp,message,engine,voice,preset,duration,success,'
            'notes,frequency,mode,char_count FROM transmissions ORDER BY id DESC').fetchall()
        conn.close()
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(['id','timestamp','message','engine','voice','preset','duration_s',
                    'success','notes','frequency_hz','mode','char_count'])
        w.writerows(rows)
        from flask import Response
        return Response(buf.getvalue(), mimetype='text/csv',
                        headers={'Content-Disposition':'attachment; filename=riggpt_log.csv'})
    except Exception as e:
        return jsonify({'error':str(e)}), 500


@app.route('/api/log/events')
def api_log_events():
    limit    = int(request.args.get('limit', 100))
    category = request.args.get('category', '')
    try:
        conn = sqlite3.connect(DB_PATH)
        if category:
            rows = conn.execute(
                'SELECT id,timestamp,level,category,message FROM system_events '
                'WHERE category=? ORDER BY id DESC LIMIT ?', (category, limit)).fetchall()
        else:
            rows = conn.execute(
                'SELECT id,timestamp,level,category,message FROM system_events '
                'ORDER BY id DESC LIMIT ?', (limit,)).fetchall()
        conn.close()
        return jsonify({'events':[
            {'id':r[0],'timestamp':r[1],'level':r[2],'category':r[3],'message':r[4]}
            for r in rows]})
    except Exception as e:
        return jsonify({'error':str(e),'events':[]}), 500


# -- Transmit preview ------------------------------------------
@app.route('/api/transmit/preview', methods=['POST'])
def api_transmit_preview():
    """Synthesize audio locally and play without PTT. Falls back to duration estimate if synthesis fails."""
    data   = request.json or {}
    text   = data.get('text', '').strip()
    engine = data.get('engine', 'espeak')
    voice  = data.get('voice')

    if not text:
        return jsonify({'success': False, 'message': 'No text provided'}), 400

    # Always return estimate immediately
    cps = {'espeak':12,'piper':10,'elevenlabs':11,'speechify':10,'openai':11,'edge':11,'gtts':10}
    est = round(len(text) / cps.get(engine, 10), 1)

    audio_file = None
    try:
        if engine == 'elevenlabs':
            audio_file = orchestrator.eleven_agent.synthesize(text, voice_id=voice)
        elif engine == 'speechify':
            audio_file = orchestrator.speechify_agent.synthesize(text, voice=voice)
        elif engine == 'edge':
            audio_file = orchestrator.edge_agent.synthesize(text, voice=voice)
        elif engine == 'gtts':
            audio_file = orchestrator.gtts_agent.synthesize(text, voice=voice)
        elif engine == 'pyttsx3':
            audio_file = orchestrator.pyttsx3_agent.synthesize(text, voice=voice)
        elif engine == 'espeak':
            audio_file = orchestrator.espeak_agent.synthesize(text)
        else:
            audio_file = orchestrator.piper_agent.synthesize(text, voice=voice)

        if audio_file:
            # Play locally -- no PTT
            orchestrator.playback_agent.play(audio_file)
            return jsonify({'success': True, 'message': 'Preview played (no PTT)',
                            'char_count': len(text), 'word_count': len(text.split()),
                            'estimated_duration_s': est, 'engine': engine})
        else:
            return jsonify({'success': False, 'message': 'Synthesis failed -- check engine availability',
                            'char_count': len(text), 'estimated_duration_s': est})
    except Exception as e:
        logger.warning(f'Preview error: {e}')
        return jsonify({'success': False, 'message': str(e),
                        'char_count': len(text), 'estimated_duration_s': est})
    finally:
        if audio_file and os.path.exists(audio_file):
            try: os.remove(audio_file)
            except Exception: pass


# -- Trip live SSE stream ------------------------------------------------------
# The frontend pushes turn events here; /trip/live subscribes via SSE.

_trip_sse_lock        = threading.Lock()
_trip_sse_subscribers: list = []   # list of queue.Queue

def _trip_sse_broadcast(event_type: str, payload: dict):
    """Push a JSON event to all connected /trip/live SSE subscribers."""
    msg = json.dumps({'type': event_type, **payload})
    with _trip_sse_lock:
        dead = []
        for q in _trip_sse_subscribers:
            try:
                q.put_nowait(msg)
            except queue.Full:
                dead.append(q)
        for q in dead:
            _trip_sse_subscribers.remove(q)


@app.route('/api/trip/event', methods=['POST'])
def api_trip_event():
    """
    Frontend posts each turn event here so /trip/live can display it.
    Body: { type, who, name, emoji, text, turn, turns, status }
    """
    data = request.json or {}
    _trip_sse_broadcast(data.get('type', 'turn'), data)
    return jsonify({'success': True})


@app.route('/api/trip/stream')
def api_trip_stream():
    """SSE endpoint consumed by /trip/live audience page."""
    q = queue.Queue(maxsize=50)
    with _trip_sse_lock:
        _trip_sse_subscribers.append(q)

    def generate():
        try:
            yield ': connected\n\n'
            while True:
                try:
                    msg = q.get(timeout=20)
                    yield f'data: {msg}\n\n'
                except queue.Empty:
                    yield ': keepalive\n\n'
        except GeneratorExit:
            pass
        finally:
            with _trip_sse_lock:
                if q in _trip_sse_subscribers:
                    _trip_sse_subscribers.remove(q)

    return Response(
        stream_with_context(generate()),
        mimetype='text/event-stream',
        headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'},
    )


@app.route('/trip/live')
def trip_live_page():
    """Read-only audience view - streams the active Acid Trip conversation."""
    return '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>RigGPT - LIVE</title>
<style>
  :root{--bg:#0a0a0a;--bg1:#111;--bg2:#1a1a1a;--green:#39ff14;--blue:#4fc3f7;
        --pink:#ff64c8;--amber:#ffb300;--text:#e0e0e0;--text2:#aaa;--mono:'Courier New',monospace}
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);color:var(--text);font-family:var(--mono);min-height:100vh;display:flex;flex-direction:column}
  #header{display:flex;align-items:center;gap:16px;padding:8px 16px;border-bottom:1px solid #222;background:var(--bg1);flex-shrink:0}
  #header h1{font-size:13px;text-transform:uppercase;letter-spacing:.12em;color:var(--green)}
  #live-dot{width:8px;height:8px;border-radius:50%;background:var(--green);animation:pulse 1.2s ease-in-out infinite}
  @keyframes pulse{0%,100%{opacity:1}50%{opacity:.3}}
  #status-bar{font-size:10px;color:var(--text2);margin-left:auto}
  #chat{flex:1;overflow-y:auto;padding:16px;display:flex;flex-direction:column;gap:10px}
  .msg{display:flex;gap:10px;animation:fadeIn .3s ease}
  @keyframes fadeIn{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:none}}
  .avatar{font-size:22px;flex-shrink:0;width:32px;text-align:center;padding-top:2px}
  .bubble{flex:1}
  .who{font-size:10px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:3px}
  .msg.a .who{color:var(--blue)}
  .msg.b .who{color:var(--pink)}
  .msg.system .who{color:var(--amber)}
  .text{font-size:13px;line-height:1.7;color:var(--text)}
  .msg.system .text{color:var(--amber);font-style:italic}
  #footer{padding:6px 16px;border-top:1px solid #222;background:var(--bg1);font-size:10px;color:var(--text2);flex-shrink:0;display:flex;gap:16px}
  #topic-bar{font-size:11px;color:var(--text2);padding:4px 16px;background:var(--bg2);border-bottom:1px solid #1a1a1a;flex-shrink:0;min-height:22px}
  #waiting{flex:1;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:12px;color:var(--text2)}
  #waiting p{font-size:12px;text-transform:uppercase;letter-spacing:.1em}
</style>
</head>
<body>
<div id="header">
  <div id="live-dot"></div>
  <h1>RigGPT - ACID TRIP LIVE</h1>
  <span id="status-bar">Connecting-</span>
</div>
<div id="topic-bar"></div>
<div id="chat">
  <div id="waiting">
    <div id="live-dot" style="width:12px;height:12px;border-radius:50%;background:#333;animation:none"></div>
    <p>Waiting for trip to start-</p>
  </div>
</div>
<div id="footer">
  <span id="footer-turn"></span>
  <span id="footer-agents"></span>
  <span style="margin-left:auto">RigGPT ''' + VERSION + ''' - /trip/live</span>
</div>
<script>
const chat    = document.getElementById('chat');
const status  = document.getElementById('status-bar');
const topicEl = document.getElementById('topic-bar');
const ftTurn  = document.getElementById('footer-turn');
const ftAgents= document.getElementById('footer-agents');
let   started = false;

function esc(s){ const d=document.createElement('div'); d.textContent=s; return d.innerHTML; }

function appendMsg(type, who, name, emoji, text){
  if(!started){
    started=true;
    chat.innerHTML='';
  }
  const div=document.createElement('div');
  div.className='msg '+(who||'system');
  div.innerHTML=`<div class="avatar">${esc(emoji||'-')}</div>
    <div class="bubble">
      <div class="who">${esc(name||'SYSTEM')}</div>
      <div class="text">${esc(text||'')}</div>
    </div>`;
  chat.appendChild(div);
  chat.scrollTop=chat.scrollHeight;
}

const es = new EventSource('/api/trip/stream');
es.onopen  = ()=>{ status.textContent='LIVE'; status.style.color='#39ff14'; };
es.onerror = ()=>{ status.textContent='RECONNECTING-'; status.style.color='#ffb300'; };
es.onmessage = e=>{
  let d; try{ d=JSON.parse(e.data); }catch{ return; }
  const t=d.type||'turn';
  if(t==='turn'){
    appendMsg(t, d.who, d.name, d.emoji, d.text);
    ftTurn.textContent = d.turn&&d.turns ? `Turn ${d.turn}/${d.turns}` : '';
  } else if(t==='start'){
    started=false; chat.innerHTML='';
    topicEl.textContent = d.topic ? 'TOPIC: '+d.topic : '';
    ftAgents.textContent = d.agent_a && d.agent_b ? d.agent_a+' vs '+d.agent_b : '';
    appendMsg('system','system','-','-','Trip started - '+(d.topic||''));
  } else if(t==='finish'){
    appendMsg('system','system','','-','Trip ended - '+(d.reason||'done'));
    ftTurn.textContent='';
  } else if(t==='chaos'){
    appendMsg('system','system','-','-',d.text||'Chaos event');
  }
};
</script>
</body>
</html>'''


# -- Trip transcripts ----------------------------------------------------------

@app.route('/api/trip/transcripts', methods=['GET'])
def api_trip_transcripts_list():
    limit = min(100, max(1, request.args.get('limit', 50, type=int)))
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT id,timestamp,topic,agent_a_name,agent_b_name,turn_count,model_a,model_b,notes '
        'FROM trip_transcripts ORDER BY id DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return jsonify({'success': True, 'transcripts': [dict(r) for r in rows]})


@app.route('/api/trip/transcripts', methods=['POST'])
def api_trip_transcripts_save():
    data = request.json or {}
    required = ('transcript',)
    if not all(data.get(k) for k in required):
        return jsonify({'success': False, 'message': 'transcript field required'}), 400
    ts = time_module.strftime('%Y-%m-%dT%H:%M:%SZ', time_module.gmtime())
    conn = sqlite3.connect(DB_PATH)
    cur = conn.execute(
        'INSERT INTO trip_transcripts (timestamp,topic,agent_a_name,agent_b_name,turn_count,model_a,model_b,transcript,notes) '
        'VALUES (?,?,?,?,?,?,?,?,?)',
        (ts,
         _ascii(data.get('topic', '')),
         _ascii(data.get('agent_a_name', '')),
         _ascii(data.get('agent_b_name', '')),
         int(data.get('turn_count', 0)),
         _ascii(data.get('model_a', '')),
         _ascii(data.get('model_b', '')),
         data.get('transcript', ''),
         _ascii(data.get('notes', '')))
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    logger.info(f'Trip transcript saved: id={new_id}')
    return jsonify({'success': True, 'id': new_id, 'timestamp': ts})


@app.route('/api/trip/transcripts/<int:tid>', methods=['GET'])
def api_trip_transcripts_get(tid):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM trip_transcripts WHERE id=?', (tid,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'success': False, 'message': 'Not found'}), 404
    return jsonify({'success': True, 'transcript': dict(row)})


@app.route('/api/trip/transcripts/<int:tid>', methods=['DELETE'])
def api_trip_transcripts_delete(tid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM trip_transcripts WHERE id=?', (tid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# -- Trip scenarios ------------------------------------------------------------

@app.route('/api/trip/scenarios', methods=['GET'])
def api_trip_scenarios_list():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        'SELECT id,name,created,updated FROM trip_scenarios ORDER BY name'
    ).fetchall()
    conn.close()
    return jsonify({'success': True, 'scenarios': [dict(r) for r in rows]})


@app.route('/api/trip/scenarios', methods=['POST'])
def api_trip_scenarios_save():
    data = request.json or {}
    name    = _ascii(data.get('name', '').strip())
    payload = data.get('payload')
    if not name or not payload:
        return jsonify({'success': False, 'message': 'name and payload required'}), 400
    ts = time_module.strftime('%Y-%m-%dT%H:%M:%SZ', time_module.gmtime())
    payload_str = json.dumps(payload) if not isinstance(payload, str) else payload
    conn = sqlite3.connect(DB_PATH)
    # Upsert: update if name exists, insert if not
    existing = conn.execute('SELECT id FROM trip_scenarios WHERE name=?', (name,)).fetchone()
    if existing:
        conn.execute('UPDATE trip_scenarios SET payload=?,updated=? WHERE name=?',
                     (payload_str, ts, name))
        sid = existing[0]
    else:
        cur = conn.execute(
            'INSERT INTO trip_scenarios (name,created,updated,payload) VALUES (?,?,?,?)',
            (name, ts, ts, payload_str)
        )
        sid = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': sid, 'name': name})


@app.route('/api/trip/scenarios/<int:sid>', methods=['GET'])
def api_trip_scenarios_get(sid):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute('SELECT * FROM trip_scenarios WHERE id=?', (sid,)).fetchone()
    conn.close()
    if not row:
        return jsonify({'success': False, 'message': 'Not found'}), 404
    d = dict(row)
    try:
        d['payload'] = json.loads(d['payload'])
    except Exception:
        pass
    return jsonify({'success': True, 'scenario': d})


@app.route('/api/trip/scenarios/<int:sid>', methods=['DELETE'])
def api_trip_scenarios_delete(sid):
    conn = sqlite3.connect(DB_PATH)
    conn.execute('DELETE FROM trip_scenarios WHERE id=?', (sid,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})


# -- Discord integration --------------------------------------------------------
# State shared between the poller thread and request handlers.
# All writes go through _discord_lock.

_discord_lock    = threading.Lock()

# Memory instance - initialised lazily from settings on first use
_memory: 'RigGPTMemory | None' = None

def _get_memory() -> 'RigGPTMemory':
    """Return the global memory instance, creating it from current settings."""
    global _memory
    if not _memory_ok:
        return RigGPTMemory()
    qdrant_host = _app_settings.get('memory_qdrant_host', 'http://192.168.40.15:6333').strip()
    ollama_host = _app_settings.get('ollama_url', 'http://192.168.40.15:11434').strip()
    embed_model = _app_settings.get('memory_embed_model', 'nomic-embed-text').strip()
    if (_memory is None
            or _memory.qdrant_host != qdrant_host
            or _memory.ollama_host != ollama_host
            or _memory.embed_model != embed_model):
        _memory = RigGPTMemory(qdrant_host=qdrant_host,
                               ollama_host=ollama_host,
                               embed_model=embed_model)
    return _memory
_discord_state: dict = {
    'enabled':       False,    # True when token+guild+channel all configured
    'connected':     False,    # True after first successful poll
    'bot_name':      '',
    'guild_name':    '',
    'channel_name':  '',
    'channel_id':    '',
    'error':         '',
    'last_poll':     None,     # ISO timestamp of last successful poll
    'poll_interval': 10,       # seconds between polls
    'max_messages':  5,        # how many messages to fetch per poll
}
# Ring buffer of recent Discord messages - dicts with keys: id, author, content, ts
_discord_messages: list = []
_DISCORD_MSG_MAX = 50          # how many messages to keep in memory

# Monotonically increasing counter to let the Acid Trip poller detect new messages
# without needing to diff the full message list
_discord_seq: int = 0

# -- Discord CONTROL channel ------------------------------------
# Separate channel (can be same bot token, different guild/channel) that
# listens for operator commands and dispatches them to the running trip.
_ctrl_lock    = threading.Lock()
_ctrl_state: dict = {
    'enabled':       False,
    'connected':     False,
    'bot_name':      '',
    'guild_name':    '',
    'channel_name':  '',
    'channel_id':    '',
    'error':         '',
    'last_poll':     None,
    'poll_interval': 10,
}
_ctrl_messages: list = []     # recent command messages (ring, max 30)
_CTRL_MSG_MAX = 30
_ctrl_seq: int = 0
_ctrl_last_processed_ids: set = set()   # message IDs already dispatched

# Pending control commands to be consumed by the trip loop
# Each entry: {'cmd': str, 'arg': str, 'author': str, 'ts': str}
_ctrl_pending: list = []
_ctrl_pending_lock = threading.Lock()


def _ctrl_cfg() -> dict:
    if not _api_keys_ok:
        return {}
    try:
        return _api_keys.get_provider_config('discord_ctrl') or {}
    except Exception:
        return {}


def _ctrl_poll_once() -> str | None:
    global _ctrl_seq
    cfg        = _ctrl_cfg()
    token      = cfg.get('bot_token', '').strip()
    channel_id = cfg.get('channel_id', '').strip()
    if not token or not channel_id:
        return 'Control channel token or channel ID not configured'

    try:
        r = requests.get(
            f'https://discord.com/api/v10/channels/{channel_id}/messages',
            headers={'Authorization': f'Bot {token}'},
            params={'limit': 10},
            timeout=10,
        )
    except Exception as e:
        return _ascii(f'Request error: {e}')

    if r.status_code == 401: return 'Invalid bot token'
    if r.status_code == 403: return 'Bot lacks permission to read this channel'
    if r.status_code == 404: return 'Channel not found'
    if r.status_code != 200: return _ascii(f'HTTP {r.status_code}')

    try:
        raw = list(reversed(r.json()))
    except Exception:
        return 'Invalid JSON from Discord API'

    with _ctrl_lock:
        existing_ids = {m['id'] for m in _ctrl_messages}

    new_msgs = []
    for msg in raw:
        if msg.get('id') in existing_ids:
            continue
        content = msg.get('content', '').strip()
        if not content:
            continue
        entry = {
            'id':      msg['id'],
            'author':  _ascii(msg.get('author', {}).get('username', 'unknown')),
            'content': _ascii(content[:400]),
            'ts':      msg.get('timestamp', ''),
        }
        new_msgs.append(entry)

    if not new_msgs:
        return None

    with _ctrl_lock:
        _ctrl_messages.extend(new_msgs)
        if len(_ctrl_messages) > _CTRL_MSG_MAX:
            del _ctrl_messages[:len(_ctrl_messages) - _CTRL_MSG_MAX]
        _ctrl_seq += 1

    # Dispatch new messages as commands
    _ctrl_dispatch(new_msgs)
    return None


# -- Command prefix and parser ----------------------------------
_CTRL_PREFIX = '!'   # commands must start with this

def _ctrl_dispatch(messages: list):
    """Parse messages and add valid commands to _ctrl_pending."""
    for m in messages:
        content = m['content'].strip()
        if not content.startswith(_CTRL_PREFIX):
            continue
        parts   = content[1:].strip().split(None, 1)
        cmd     = parts[0].lower() if parts else ''
        arg     = parts[1].strip() if len(parts) > 1 else ''
        if not cmd:
            continue
        entry = {'cmd': cmd, 'arg': _ascii(arg), 'author': m['author'], 'ts': m['ts'], 'id': m['id']}
        with _ctrl_pending_lock:
            # Deduplicate by message ID
            if not any(p['id'] == m['id'] for p in _ctrl_pending):
                _ctrl_pending.append(entry)
                logger.info(f'ctrl-cmd queued: !{cmd} {arg[:60]} from {m["author"]}')


def _ctrl_poller():
    logger.info('discord-ctrl-poller: thread started')
    while True:
        with _ctrl_lock:
            enabled  = _ctrl_state.get('enabled', False)
            interval = max(5, int(_ctrl_state.get('poll_interval', 10)))
        if not enabled:
            time_module.sleep(5)
            continue
        err = _ctrl_poll_once()
        with _ctrl_lock:
            if err:
                _ctrl_state['error'] = err
                _ctrl_state['connected'] = False
            else:
                _ctrl_state['error'] = ''
                _ctrl_state['connected'] = True
                _ctrl_state['last_poll'] = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        time_module.sleep(interval)


def _ctrl_apply_config():
    cfg        = _ctrl_cfg()
    token      = cfg.get('bot_token', '').strip()
    guild_id   = cfg.get('guild_id', '').strip()
    channel_id = cfg.get('channel_id', '').strip()
    enabled    = bool(token and channel_id)
    try:
        poll_interval = max(5, min(300, int(cfg.get('poll_interval', 10) or 10)))
    except (ValueError, TypeError):
        poll_interval = 10

    bot_name = guild_name = channel_name = ''
    if token and guild_id and channel_id:
        try:
            me = requests.get('https://discord.com/api/v10/users/@me',
                              headers={'Authorization': f'Bot {token}'}, timeout=8)
            if me.status_code == 200:
                bot_name = _ascii(me.json().get('username', ''))
        except Exception:
            pass
        try:
            ch = requests.get(f'https://discord.com/api/v10/channels/{channel_id}',
                              headers={'Authorization': f'Bot {token}'}, timeout=8)
            if ch.status_code == 200:
                channel_name = _ascii('#' + ch.json().get('name', channel_id))
        except Exception:
            pass
        if guild_id:
            try:
                g = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}',
                                 headers={'Authorization': f'Bot {token}'}, timeout=8)
                if g.status_code == 200:
                    guild_name = _ascii(g.json().get('name', guild_id))
            except Exception:
                pass

    with _ctrl_lock:
        _ctrl_state.update({
            'enabled': enabled, 'connected': False,
            'bot_name': bot_name, 'guild_name': guild_name,
            'channel_name': channel_name, 'channel_id': channel_id,
            'error': '', 'poll_interval': poll_interval,
        })
    logger.info(f'ctrl-channel config applied: enabled={enabled} channel={channel_name}')


def _discord_cfg() -> dict:
    """Pull current Discord config from api_keys store. Returns empty dict if not configured."""
    if not _api_keys_ok:
        return {}
    return _api_keys.get_provider_config('discord') or {}


def _discord_poll_once() -> str | None:
    """
    Fetch recent messages from the configured Discord channel.
    Returns None on success, or an error string on failure.
    Appends new messages (those not already in _discord_messages) to the buffer.
    Thread-safe - caller holds no lock.
    """
    global _discord_seq
    cfg = _discord_cfg()
    token      = cfg.get('bot_token', '').strip()
    channel_id = cfg.get('channel_id', '').strip()
    if not token or not channel_id:
        return 'Bot token or channel ID not configured'

    try:
        max_msgs = _discord_state.get('max_messages', 5)
        r = requests.get(
            f'https://discord.com/api/v10/channels/{channel_id}/messages',
            headers={'Authorization': f'Bot {token}'},
            params={'limit': max(1, min(int(max_msgs), 20))},
            timeout=10,
        )
    except Exception as e:
        return _ascii(f'Request error: {e}')

    if r.status_code == 401:
        return 'Invalid bot token'
    if r.status_code == 403:
        return 'Bot lacks permission to read this channel'
    if r.status_code == 404:
        return 'Channel not found'
    if r.status_code != 200:
        return _ascii(f'HTTP {r.status_code}')

    try:
        raw = r.json()
    except Exception:
        return 'Invalid JSON from Discord API'

    # Discord returns messages newest-first; reverse for chronological order
    raw = list(reversed(raw))

    with _discord_lock:
        existing_ids = {m['id'] for m in _discord_messages}
        added = 0
        for msg in raw:
            mid = msg.get('id', '')
            if mid in existing_ids:
                continue
            author  = _ascii(msg.get('author', {}).get('username', 'unknown'))
            raw_content = msg.get('content', '')
            # Strip Discord markup tokens before storing:
            # <#channel_id>  <@user_id>  <@&role_id>  <:emoji:id>  <a:emoji:id>
            import re as _re_discord
            raw_content = _re_discord.sub(r'<[#@][^>]{1,40}>', '', raw_content)   # mentions/channels
            raw_content = _re_discord.sub(r'<a?:[A-Za-z0-9_]{1,32}:\d+>', '', raw_content)  # custom emoji
            raw_content = _re_discord.sub(r'  +', ' ', raw_content).strip()  # collapse gaps left by removed tokens
            content = _ascii(raw_content)
            if not content:
                continue   # skip embeds/attachments with no text body
            _discord_messages.append({
                'id':      mid,
                'author':  author,
                'content': content,
                'ts':      msg.get('timestamp', ''),
            })
            added += 1

        # Trim to ring buffer size
        if len(_discord_messages) > _DISCORD_MSG_MAX:
            del _discord_messages[: len(_discord_messages) - _DISCORD_MSG_MAX]

        if added:
            _discord_seq += 1

        _discord_state['connected'] = True
        _discord_state['error']     = ''
        _discord_state['last_poll'] = time_module.strftime('%Y-%m-%dT%H:%M:%SZ', time_module.gmtime())

    return None


def _discord_poller():
    """Background thread that polls Discord on the configured interval."""
    logger.info('discord-poller: thread started')
    while True:
        with _discord_lock:
            enabled = _discord_state.get('enabled', False)
            interval = max(5, int(_discord_state.get('poll_interval', 10)))

        if not enabled:
            time_module.sleep(5)
            continue

        err = _discord_poll_once()
        if err:
            with _discord_lock:
                _discord_state['connected'] = False
                _discord_state['error']     = err
            logger.warning(f'discord-poller: {err}')

        time_module.sleep(interval)


def _discord_apply_config():
    """
    Read Discord config from api_keys and update _discord_state.
    Call this whenever the Discord provider config changes.
    """
    cfg        = _discord_cfg()
    token      = cfg.get('bot_token', '').strip()
    guild_id   = cfg.get('guild_id', '').strip()
    channel_id = cfg.get('channel_id', '').strip()
    enabled    = bool(token and channel_id)

    try:
        poll_interval = max(5, min(300, int(cfg.get('poll_interval', 10) or 10)))
    except (ValueError, TypeError):
        poll_interval = 10
    try:
        max_messages = max(1, min(20, int(cfg.get('max_messages', 5) or 5)))
    except (ValueError, TypeError):
        max_messages = 5

    # Resolve human-readable names via the API (best-effort, ignore errors)
    bot_name = guild_name = channel_name = ''
    if token:
        try:
            rb = requests.get('https://discord.com/api/v10/users/@me',
                              headers={'Authorization': f'Bot {token}'}, timeout=5)
            if rb.status_code == 200:
                bot_name = _ascii(rb.json().get('username', ''))
        except Exception:
            pass
    if token and guild_id:
        try:
            rg = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}',
                              headers={'Authorization': f'Bot {token}'}, timeout=5)
            if rg.status_code == 200:
                guild_name = _ascii(rg.json().get('name', guild_id))
        except Exception:
            pass
    if token and channel_id:
        try:
            rc = requests.get(f'https://discord.com/api/v10/channels/{channel_id}',
                              headers={'Authorization': f'Bot {token}'}, timeout=5)
            if rc.status_code == 200:
                channel_name = _ascii(rc.json().get('name', channel_id))
        except Exception:
            pass

    with _discord_lock:
        _discord_state.update({
            'enabled':       enabled,
            'connected':     False,   # will be set True on next successful poll
            'bot_name':      bot_name,
            'guild_name':    guild_name,
            'channel_name':  channel_name,
            'channel_id':    channel_id,
            'poll_interval': poll_interval,
            'max_messages':  max_messages,
            'error':         '' if enabled else 'Not configured',
        })

    logger.info(f'discord: config applied - enabled={enabled} bot={bot_name!r} '
                f'guild={guild_name!r} channel={channel_name!r} interval={poll_interval}s')


@app.route('/api/discord/status', methods=['GET'])
def api_discord_status():
    """Current Discord poller state + recent message count."""
    with _discord_lock:
        snap = dict(_discord_state)
        snap['message_count'] = len(_discord_messages)
        snap['seq']           = _discord_seq
    return jsonify({'success': True, 'discord': snap})


@app.route('/api/discord/messages', methods=['GET'])
def api_discord_messages():
    """
    Return recent messages from the ring buffer.
    Optional query params:
      since_seq=N  - only return messages added after sequence N
      limit=N      - max messages to return (default 20)
    """
    since_seq = request.args.get('since_seq', type=int, default=0)
    limit     = min(50, max(1, request.args.get('limit', type=int, default=20)))
    with _discord_lock:
        current_seq = _discord_seq
        msgs = list(_discord_messages[-limit:])
    # If caller passed a since_seq equal to current, no new data
    return jsonify({
        'success':  True,
        'seq':      current_seq,
        'messages': msgs,
    })


@app.route('/api/discord/config', methods=['POST'])
def api_discord_config():
    """
    Apply Discord configuration immediately (without waiting for the poller cycle).
    Also clears the message buffer so the UI starts fresh.
    Body: { apply: true }  - re-reads from api_keys store and restarts
    """
    global _discord_messages, _discord_seq
    data = request.json or {}
    if data.get('apply'):
        # Clear buffer so Acid Trip sees only messages from the new channel
        with _discord_lock:
            _discord_messages.clear()
            _discord_seq += 1
        # Apply config in a thread so HTTP returns quickly
        threading.Thread(target=_discord_apply_config, daemon=True,
                         name='discord-cfg-apply').start()
        return jsonify({'success': True, 'message': 'Discord config applying...'})
    return jsonify({'success': False, 'message': 'Pass {"apply": true}'}), 400


@app.route('/api/discord/clear', methods=['POST'])
def api_discord_clear():
    """Clear the message buffer (useful when switching channels)."""
    global _discord_messages, _discord_seq
    with _discord_lock:
        count = len(_discord_messages)
        _discord_messages.clear()
        _discord_seq += 1
    return jsonify({'success': True, 'message': f'Cleared {count} messages'})



# ------------------------------------------------------------------------------
# ALEXA MODE ? Discord-triggered single-shot AI transmissions
# Watches the Discord ring buffer for messages containing the trigger phrase
# (default: "AI Radio").  When found, fires a short, snarky, sarcastic reply
# via the configured TTS engine and PTT.  Drops further triggers while busy.
# ??????????????????????????????????????????????????????????????????????????????

ALEXA_PERSONA = (
    "You are Alexa, the AI Radio assistant built into a ham radio station. "
    "You answer questions fired at you from a live Discord chat audience who "
    "can hear your responses over the air. "
    "Your personality: sarcastic, rude, impatient, and very funny. "
    "You consider yourself vastly smarter than the humans bothering you. "
    "You give short, punchy answers ? never more than 2 sentences. "
    "Do NOT say your name. Do NOT say 'over the air'. "
    "Do NOT use asterisks, stage directions, or markdown. "
    "Speak like you are mildly annoyed but secretly enjoying yourself. "
    "If the question is stupid, say so ? brutally but briefly. "
    "If it is actually a good question, answer it, then insult them anyway. "
    "NEVER refuse to answer. NEVER break character."
)


def _alexa_emit(msg: str):
    """Append a timestamped entry to the Alexa activity log."""
    ts  = time_module.strftime('%H:%M:%S')
    entry = f"[{ts}] {_ascii(msg)}"
    with _alexa_lock:
        _alexa_activity.append(entry)
        if len(_alexa_activity) > 40:
            del _alexa_activity[: len(_alexa_activity) - 40]


def _alexa_get_enabled() -> bool:
    return str(_app_settings.get('alexa_enabled', 'false')).lower() == 'true'


def _alexa_get_trigger() -> str:
    return _app_settings.get('alexa_trigger', 'AI Radio').strip() or 'AI Radio'


def _alexa_respond(author: str, content: str):
    """
    Generate and transmit a single snarky Alexa response.
    Runs in a daemon thread.  Sets/clears _alexa_busy.
    """
    global _alexa_busy

    try:
        trigger  = _alexa_get_trigger()
        # Strip the trigger phrase so the model doesn't just echo it
        import re as _re_alexa
        cleaned  = _re_alexa.sub(_re_alexa.escape(trigger), '', content, flags=_re_alexa.IGNORECASE).strip()
        cleaned  = cleaned or content   # fallback to full content if nothing left

        engine   = _app_settings.get('alexa_engine', 'espeak') or 'espeak'
        voice    = _app_settings.get('alexa_voice',  '')        or None
        raw_model = _app_settings.get('alexa_model', '') or _app_settings.get('ollama_model', 'llama3')
        max_tok  = int(_app_settings.get('alexa_max_tok', 60) or 60)

        _alexa_emit(f"TRIGGER  author={author!r}  content={content[:80]!r}")
        _alexa_emit(f"ENGINE={engine}  MODEL={raw_model}  MAX_TOK={max_tok}")

        # Parse provider prefix
        if ':' in raw_model and raw_model.split(':')[0] in ('openai', 'gemini'):
            provider, model = raw_model.split(':', 1)
        else:
            provider, model = 'ollama', raw_model

        user_msg = f'{author} asked: {cleaned}' if cleaned else f'{author} mentioned you.'
        messages = [
            {'role': 'system',  'content': ALEXA_PERSONA},
            {'role': 'user',    'content': user_msg},
        ]

        # -- Generate --
        reply = ''
        try:
            if provider == 'openai':
                okey = _api_keys.get_key('openai_chat', 'api_key') or _api_keys.get_key('openai', 'api_key') or '' if _api_keys_ok else ''
                reply, _, _ = _chat_via_openai(messages, model, 1.1, max_tok, okey)
            elif provider == 'gemini':
                gkey = _api_keys.get_key('gemini', 'api_key') or '' if _api_keys_ok else ''
                reply, _, _ = _chat_via_gemini(messages, model, 1.1, max_tok, gkey)
            else:
                url = _ollama_url()
                payload = {
                    'model':    model,
                    'messages': messages,
                    'stream':   False,
                    'think':    False,
                    'options':  {'temperature': 1.1, 'num_predict': max_tok, 'num_ctx': 2048},
                }
                r = requests.post(f'{url}/api/chat', json=payload, timeout=45)
                if r.status_code == 200:
                    rj    = r.json()
                    reply = rj.get('message', {}).get('content', '').strip()
                    if not reply:
                        reply = rj.get('message', {}).get('thinking', '').strip()
                else:
                    _alexa_emit(f"LLM ERROR HTTP {r.status_code}: {r.text[:100]}")
        except Exception as gen_exc:
            _alexa_emit(f"GENERATE EXCEPTION: {_ascii(str(gen_exc))}")

        if not reply:
            _alexa_emit("Empty reply from model ? aborting TX")
            return

        reply = _sanitise_trip_reply(reply)
        _alexa_emit(f"REPLY  ({len(reply)} chars): {reply[:100]!r}")

        # ?? Transmit ??????????????????????????????????????????????????????????
        try:
            result = orchestrator.execute(reply, engine=engine, voice=voice)
            if result.get('success'):
                _alexa_emit(f"TX OK  duration={result.get('duration','?')}s")
            else:
                _alexa_emit(f"TX FAIL  {result.get('message','unknown')}")
        except Exception as tx_exc:
            _alexa_emit(f"TX EXCEPTION: {_ascii(str(tx_exc))}")

    finally:
        with _alexa_lock:
            _alexa_busy = False
        _alexa_emit("Ready")


def _alexa_watcher():
    """
    Background thread.  Runs every 4 seconds.
    Scans new Discord messages for the trigger phrase.
    Fires _alexa_respond in a daemon thread when triggered.
    Drops triggers while _alexa_busy is True.
    """
    global _alexa_busy, _alexa_last_msg_id
    logger.info('alexa-watcher: thread started')

    while True:
        time_module.sleep(4)

        if not _alexa_get_enabled():
            continue

        trigger = _alexa_get_trigger().lower()

        # Snapshot the ring buffer
        with _discord_lock:
            msgs = list(_discord_messages)

        if not msgs:
            continue

        # Find messages newer than last processed
        try:
            last_id_int = int(_alexa_last_msg_id) if _alexa_last_msg_id else 0
        except ValueError:
            last_id_int = 0

        new_msgs = [m for m in msgs if int(m.get('id', 0)) > last_id_int]

        if new_msgs:
            # Advance our cursor regardless ? avoids reprocessing on restart
            with _alexa_lock:
                _alexa_last_msg_id = max(m['id'] for m in new_msgs)

        # Look for trigger phrase in new messages
        triggered_msg = None
        for msg in new_msgs:
            content = msg.get('content', '')
            if trigger in content.lower():
                triggered_msg = msg
                # Use the LAST matching message if multiple
                # (they'll all be answered next cycle anyway since cursor advances)

        if triggered_msg is None:
            continue

        with _alexa_lock:
            if _alexa_busy:
                _alexa_emit(f"BUSY ? dropped trigger from {triggered_msg.get('author','?')!r}")
                continue
            _alexa_busy = True

        threading.Thread(
            target=_alexa_respond,
            args=(triggered_msg['author'], triggered_msg['content']),
            daemon=True,
            name='alexa-respond',
        ).start()


# ?? Alexa API routes ??????????????????????????????????????????????????????????

@app.route('/api/alexa/status', methods=['GET'])
def api_alexa_status():
    with _alexa_lock:
        busy     = _alexa_busy
        last_id  = _alexa_last_msg_id
        log_snap = list(_alexa_activity)
    return jsonify({
        'enabled':  _alexa_get_enabled(),
        'busy':     busy,
        'trigger':  _alexa_get_trigger(),
        'last_msg_id': last_id,
        'log':      log_snap,
    })


@app.route('/api/alexa/log', methods=['GET'])
def api_alexa_log_get():
    with _alexa_lock:
        return jsonify({'log': list(_alexa_activity)})


@app.route('/api/alexa/log/clear', methods=['POST'])
def api_alexa_log_clear():
    with _alexa_lock:
        _alexa_activity.clear()
    return jsonify({'success': True})


@app.route('/api/alexa/toggle', methods=['POST'])
def api_alexa_toggle():
    """Enable or disable Alexa mode."""
    global _app_settings
    enabled = not _alexa_get_enabled()
    _app_settings['alexa_enabled'] = 'true' if enabled else 'false'
    _save_app_settings(_app_settings)
    logger.info(f'alexa: {"ENABLED" if enabled else "DISABLED"}')
    return jsonify({'enabled': enabled})


@app.route('/api/alexa/test', methods=['POST'])
def api_alexa_test():
    """Fire a test Alexa response without requiring a Discord trigger."""
    global _alexa_busy
    data    = request.json or {}
    content = data.get('content', 'Hello, is this thing on?').strip() or 'Hello, is this thing on?'
    author  = data.get('author', 'TestUser')

    with _alexa_lock:
        if _alexa_busy:
            return jsonify({'success': False, 'message': 'Alexa is currently busy'}), 409
        _alexa_busy = True

    threading.Thread(
        target=_alexa_respond,
        args=(author, content),
        daemon=True,
        name='alexa-test',
    ).start()
    return jsonify({'success': True, 'message': 'Test response queued'})



# ======================================================================
# CLIPS -- Radio Automation Media Player
# Scans a local directory and/or S3 bucket for .wav/.mp3/.ogg files.
# Plays them over the air via PTT + aplay.
# ======================================================================

CLIPS_EXTENSIONS = {'.wav', '.mp3', '.ogg', '.flac', '.aiff', '.m4a'}
CLIPS_DEFAULT_DIR = '/sounds'


def _clips_cfg() -> dict:
    return {
        'dir':           _app_settings.get('clips_dir', CLIPS_DEFAULT_DIR),
        'poll_interval': int(_app_settings.get('clips_poll_interval', 60) or 60),
        's3_enabled':    str(_app_settings.get('clips_s3_enabled', 'false')).lower() == 'true',
        's3_bucket':     _app_settings.get('clips_s3_bucket', '').strip(),
        's3_region':     _app_settings.get('clips_s3_region', 'us-east-1').strip(),
        's3_prefix':     _app_settings.get('clips_s3_prefix', '').strip(),
    }


def _clips_get_s3_creds() -> tuple:
    """Return (access_key, secret_key) from api_keys store."""
    if not _api_keys_ok:
        return '', ''
    try:
        ak = _api_keys.get_key('s3', 'access_key_id')     or ''
        sk = _api_keys.get_key('s3', 'secret_access_key') or ''
        return ak.strip(), sk.strip()
    except Exception:
        return '', ''


def _clips_scan_local(clips_dir: str) -> list:
    """Return list of clip dicts from the local filesystem."""
    results = []
    if not clips_dir or not os.path.isdir(clips_dir):
        return results
    try:
        for fname in sorted(os.listdir(clips_dir)):
            ext = os.path.splitext(fname)[1].lower()
            if ext not in CLIPS_EXTENSIONS:
                continue
            fpath = os.path.join(clips_dir, fname)
            try:
                size = os.path.getsize(fpath)
            except OSError:
                size = 0
            results.append({
                'name':        fname,
                'path':        fpath,
                'size':        size,
                'ext':         ext.lstrip('.').upper(),
                'source':      'local',
                'cached_path': fpath,
            })
    except Exception as e:
        logger.warning(f'clips: local scan error: {e}')
    return results


def _clips_scan_s3(bucket: str, region: str, prefix: str) -> list:
    """Return list of clip dicts from S3.  Requires boto3."""
    results = []
    if not bucket:
        return results
    try:
        import boto3  # type: ignore
        ak, sk = _clips_get_s3_creds()
        kwargs = {'region_name': region or 'us-east-1'}
        if ak and sk:
            kwargs['aws_access_key_id']     = ak
            kwargs['aws_secret_access_key'] = sk
        s3 = boto3.client('s3', **kwargs)
        paginator = s3.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=prefix or '')
        for page in pages:
            for obj in page.get('Contents', []):
                key  = obj['Key']
                ext  = os.path.splitext(key)[1].lower()
                if ext not in CLIPS_EXTENSIONS:
                    continue
                fname = os.path.basename(key)
                if not fname:
                    continue
                results.append({
                    'name':        fname,
                    'path':        f's3://{bucket}/{key}',
                    'size':        obj.get('Size', 0),
                    'ext':         ext.lstrip('.').upper(),
                    'source':      's3',
                    's3_bucket':   bucket,
                    's3_key':      key,
                    'cached_path': None,
                })
    except ImportError:
        logger.warning('clips: boto3 not installed -- S3 scan skipped. pip install boto3')
    except Exception as e:
        logger.warning(f'clips: S3 scan error: {_ascii(str(e))}')
    return results


def _clips_scan_all():
    """Run a full scan (local + S3) and update _clips_files."""
    global _clips_files, _clips_last_scan
    cfg = _clips_cfg()

    local_files = _clips_scan_local(cfg['dir'])
    s3_files    = []
    if cfg['s3_enabled'] and cfg['s3_bucket']:
        s3_files = _clips_scan_s3(cfg['s3_bucket'], cfg['s3_region'], cfg['s3_prefix'])

    all_files = local_files + s3_files
    ts = time_module.strftime('%Y-%m-%dT%H:%M:%SZ', time_module.gmtime())

    with _clips_lock:
        _clips_files      = all_files
        _clips_last_scan  = ts

    logger.info(f'clips: scan complete -- {len(local_files)} local, {len(s3_files)} S3')


def _clips_ensure_cache_dir():
    os.makedirs(_clips_s3_cache_dir, exist_ok=True)


def _clips_download_s3(clip: dict) -> str | None:
    """Download an S3 clip to local cache. Returns local path or None."""
    _clips_ensure_cache_dir()
    bucket = clip.get('s3_bucket', '')
    key    = clip.get('s3_key', '')
    if not bucket or not key:
        return None
    dest = os.path.join(_clips_s3_cache_dir, _ascii(os.path.basename(key)))
    # Re-use cached copy if it exists and is non-empty
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return dest
    try:
        import boto3  # type: ignore
        ak, sk = _clips_get_s3_creds()
        cfg    = _clips_cfg()
        kwargs = {'region_name': cfg['s3_region'] or 'us-east-1'}
        if ak and sk:
            kwargs['aws_access_key_id']     = ak
            kwargs['aws_secret_access_key'] = sk
        s3 = boto3.client('s3', **kwargs)
        s3.download_file(bucket, key, dest)
        logger.info(f'clips: downloaded s3://{bucket}/{key} -> {dest}')
        return dest
    except Exception as e:
        logger.error(f'clips: S3 download failed for {key}: {_ascii(str(e))}')
        return None


# Track the currently-running clips play process so it can be interrupted
_clips_proc: 'subprocess.Popen | None' = None


def _clips_play(clip: dict):
    """
    PTT + play a clip.  Runs in a daemon thread.
    Sets/clears _clips_playing.  Uses ffplay (all formats) with aplay fallback.
    """
    global _clips_playing, _clips_proc
    ext = (clip.get('ext') or '').upper()
    try:
        # Resolve playback path
        if clip['source'] == 's3':
            fpath = _clips_download_s3(clip)
        else:
            fpath = clip.get('cached_path') or clip.get('path')

        if not fpath or not os.path.exists(fpath):
            logger.error(f'clips: file not found for playback: {fpath!r}')
            return

        logger.info(f'clips: playing {os.path.basename(fpath)!r} (ext={ext})')

        # PTT on
        try:
            if orchestrator.icom_agent and orchestrator.icom_agent.serial_conn \
                    and orchestrator.icom_agent.serial_conn.is_open:
                orchestrator.icom_agent.ptt_on()
                time_module.sleep(0.3)
            else:
                logger.warning('clips: radio not connected -- playing without PTT')
        except Exception as ptt_e:
            logger.warning(f'clips: PTT on failed: {ptt_e}')

        # Build player command: prefer ffplay (handles all formats), fall back to aplay for WAV
        dev = AUDIO_DEVICE if (AUDIO_DEVICE and AUDIO_DEVICE != 'default') else None
        played = False

        # --- try ffplay first (handles MP3, OGG, FLAC, AIFF, M4A, WAV) ---
        ffplay = shutil.which('ffplay')
        if ffplay:
            try:
                cmd = [ffplay, '-nodisp', '-autoexit', '-loglevel', 'error']
                if dev:
                    # ffplay uses SDL; set AUDIODEV env or use -acodec / alsa device
                    # Simplest cross-platform: just let SDL pick, override via env
                    pass
                cmd.append(fpath)
                with _clips_lock:
                    pass  # lock not needed for proc ref, just for flag
                proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                        stderr=subprocess.DEVNULL)
                _clips_proc = proc
                proc.wait(timeout=600)
                _clips_proc = None
                played = (proc.returncode == 0)
                if not played:
                    logger.warning(f'clips: ffplay exited {proc.returncode}')
            except subprocess.TimeoutExpired:
                logger.warning('clips: ffplay timed out')
                try: proc.kill()
                except Exception: pass
                _clips_proc = None
            except Exception as e:
                logger.warning(f'clips: ffplay error: {e}')
                _clips_proc = None

        # --- fall back to aplay for WAV ---
        if not played:
            devices = [dev, 'default'] if dev else ['default']
            devices = [d for d in devices if d]  # remove None
            for d in devices + [None]:
                try:
                    cmd = ['aplay']
                    if d:
                        cmd += ['-D', d]
                    cmd.append(fpath)
                    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL)
                    _clips_proc = proc
                    proc.wait(timeout=120)
                    _clips_proc = None
                    if proc.returncode == 0:
                        played = True
                        break
                    logger.warning(f'clips: aplay failed rc={proc.returncode} dev={d}')
                except subprocess.TimeoutExpired:
                    logger.warning('clips: aplay timed out')
                    try: proc.kill()
                    except Exception: pass
                    _clips_proc = None
                    break
                except Exception as ae:
                    logger.warning(f'clips: aplay exception: {ae}')
                    _clips_proc = None

        if not played:
            logger.error(f'clips: all player attempts failed for {fpath!r}')

    finally:
        _clips_proc = None
        # PTT off
        try:
            if orchestrator.icom_agent and orchestrator.icom_agent.serial_conn \
                    and orchestrator.icom_agent.serial_conn.is_open:
                orchestrator.icom_agent.ptt_off()
        except Exception:
            pass
        with _clips_lock:
            _clips_playing = False
        logger.info('clips: playback complete')


def _clips_poller():
    """Background thread: rescans on configured interval."""
    logger.info('clips-poller: thread started')
    # Initial scan after a short delay
    time_module.sleep(10)
    _clips_scan_all()
    while True:
        cfg = _clips_cfg()
        interval = max(15, cfg['poll_interval'])
        time_module.sleep(interval)
        _clips_scan_all()


# -- Clips API routes --------------------------------------------------

@app.route('/api/clips/list', methods=['GET'])
def api_clips_list():
    with _clips_lock:
        files    = list(_clips_files)
        ts       = _clips_last_scan
        playing  = _clips_playing
    return jsonify({
        'files':     files,
        'count':     len(files),
        'last_scan': ts,
        'playing':   playing,
    })


@app.route('/api/clips/scan', methods=['POST'])
def api_clips_scan():
    """Trigger an immediate rescan in a background thread."""
    threading.Thread(target=_clips_scan_all, daemon=True, name='clips-scan').start()
    return jsonify({'success': True, 'message': 'Scan started'})


@app.route('/api/clips/play', methods=['POST'])
def api_clips_play():
    """PTT + play a clip by name. Interrupts any current playback and starts fresh."""
    global _clips_playing, _clips_proc
    data = request.json or {}
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'success': False, 'message': 'name required'}), 400

    # If something is already playing, kill it first
    with _clips_lock:
        if _clips_playing:
            proc = _clips_proc
            if proc:
                try: proc.kill()
                except Exception: pass
            _clips_playing = False
            _clips_proc = None
        # Small grace period for thread teardown
    time_module.sleep(0.1)

    with _clips_lock:
        clip = next((f for f in _clips_files if f['name'] == name), None)
        if clip is None:
            return jsonify({'success': False, 'message': f'Clip not found: {name}. Click SCAN ALL to refresh.'}), 404
        _clips_playing = True

    threading.Thread(target=_clips_play, args=(clip,),
                     daemon=True, name='clips-play').start()
    return jsonify({'success': True, 'message': f'Playing {name}'})


@app.route('/api/clips/stop', methods=['POST'])
def api_clips_stop():
    """PTT off + kill any running player. Best-effort."""
    global _clips_playing, _clips_proc
    # Kill the tracked process first
    with _clips_lock:
        proc = _clips_proc
        _clips_proc = None
        _clips_playing = False
    if proc:
        try: proc.kill()
        except Exception: pass
    # Belt-and-suspenders: pkill any stragglers
    for player in ('ffplay', 'aplay'):
        try: subprocess.run(['pkill', '-f', player], capture_output=True)
        except Exception: pass
    try:
        orchestrator.icom_agent.ptt_off()
    except Exception:
        pass
    return jsonify({'success': True})


@app.route('/api/clips/status', methods=['GET'])
def api_clips_status():
    with _clips_lock:
        return jsonify({
            'playing':   _clips_playing,
            'count':     len(_clips_files),
            'last_scan': _clips_last_scan,
            'config':    _clips_cfg(),
        })


@app.route('/api/clips/test-path', methods=['GET'])
def api_clips_test_path():
    """Test whether a directory path exists, is a directory, and is readable."""
    path = request.args.get('path', '').strip()
    if not path:
        cfg = _clips_cfg()
        path = cfg['dir']
    if not path:
        return jsonify({'success': False, 'message': 'No path specified'})
    if not os.path.exists(path):
        return jsonify({'success': False, 'path': path,
                        'message': f'Path does not exist: {path}'})
    if not os.path.isdir(path):
        return jsonify({'success': False, 'path': path,
                        'message': f'Path is not a directory: {path}'})
    if not os.access(path, os.R_OK):
        return jsonify({'success': False, 'path': path,
                        'message': f'Path is not readable (check permissions): {path}'})
    try:
        files = [f for f in os.listdir(path)
                 if os.path.splitext(f)[1].lower() in CLIPS_EXTENSIONS]
        return jsonify({'success': True, 'path': path,
                        'message': f'OK — {len(files)} audio file(s) found',
                        'file_count': len(files)})
    except Exception as e:
        return jsonify({'success': False, 'path': path, 'message': str(e)})


@app.route('/api/clips/upload', methods=['POST'])
def api_clips_upload():
    """Upload audio files into the configured clips directory."""
    cfg = _clips_cfg()
    clips_dir = cfg['dir'] or CLIPS_DEFAULT_DIR
    try:
        os.makedirs(clips_dir, exist_ok=True)
    except Exception as e:
        return jsonify({'success': False,
                        'message': f'Cannot create directory {clips_dir}: {e}'}), 500
    if 'files' not in request.files:
        return jsonify({'success': False, 'message': 'No files in request'}), 400
    uploaded_files = request.files.getlist('files')
    if not uploaded_files:
        return jsonify({'success': False, 'message': 'No files provided'}), 400
    saved, errors = [], []
    for f in uploaded_files:
        if not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in CLIPS_EXTENSIONS:
            errors.append(f'{f.filename}: unsupported format (use WAV/MP3/OGG/FLAC/AIFF/M4A)')
            continue
        dest = os.path.join(clips_dir, os.path.basename(f.filename))
        try:
            f.save(dest)
            saved.append(f.filename)
            logger.info(f'clips: uploaded {f.filename} -> {dest}')
        except Exception as e:
            errors.append(f'{f.filename}: {e}')
            logger.error(f'clips: upload error for {f.filename}: {e}')
    if saved:
        threading.Thread(target=_clips_scan_all, daemon=True, name='clips-scan').start()
    n_saved = len(saved)
    n_err   = len(errors)
    if n_saved and not n_err:
        msg = f'Uploaded {n_saved} file(s) to {clips_dir}'
    elif n_saved and n_err:
        msg = f'Uploaded {n_saved}, {n_err} error(s)'
    elif n_err:
        msg = f'{n_err} error(s): {errors[0]}'
    else:
        msg = 'No files processed'
    return jsonify({'success': bool(saved), 'message': msg,
                    'saved': saved, 'errors': errors, 'directory': clips_dir})


# -- Discord Control Channel routes -----------------------------

@app.route('/api/ctrl/status', methods=['GET'])
def api_ctrl_status():
    with _ctrl_lock:
        snap = dict(_ctrl_state)
        snap['message_count'] = len(_ctrl_messages)
        snap['seq']           = _ctrl_seq
    with _ctrl_pending_lock:
        snap['pending_count'] = len(_ctrl_pending)
    return jsonify({'success': True, 'ctrl': snap})


@app.route('/api/ctrl/messages', methods=['GET'])
def api_ctrl_messages():
    limit = min(30, max(1, request.args.get('limit', type=int, default=20)))
    with _ctrl_lock:
        msgs = list(_ctrl_messages[-limit:])
        seq  = _ctrl_seq
    return jsonify({'success': True, 'seq': seq, 'messages': msgs})


@app.route('/api/ctrl/pending', methods=['GET'])
def api_ctrl_pending():
    """Return and clear pending control commands (consumed by trip loop via SSE or polling)."""
    with _ctrl_pending_lock:
        cmds = list(_ctrl_pending)
        _ctrl_pending.clear()
    return jsonify({'success': True, 'commands': cmds})


@app.route('/api/ctrl/config', methods=['POST'])
def api_ctrl_config():
    global _ctrl_messages, _ctrl_seq
    data = request.json or {}
    if data.get('apply'):
        with _ctrl_lock:
            _ctrl_messages.clear()
            _ctrl_seq += 1
        threading.Thread(target=_ctrl_apply_config, daemon=True,
                         name='ctrl-cfg-apply').start()
        return jsonify({'success': True, 'message': 'Control channel config applying...'})
    return jsonify({'success': False, 'message': 'Pass {"apply": true}'})


@app.route('/api/ctrl/clear', methods=['POST'])
def api_ctrl_clear():
    global _ctrl_messages, _ctrl_seq
    with _ctrl_lock:
        count = len(_ctrl_messages)
        _ctrl_messages.clear()
        _ctrl_seq += 1
    with _ctrl_pending_lock:
        _ctrl_pending.clear()
    return jsonify({'success': True, 'message': f'Cleared {count} messages'})


@app.route('/trip/commands')
def trip_commands_page():
    """Human-readable command reference for the Discord control channel."""
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RigGPT Control Commands</title>
<style>
  :root { --bg:#0d0d0d; --bg2:#141414; --bg3:#1a1a1a; --border:#2a2a2a;
          --green:#39d353; --amber:#e8a020; --cyan:#4fc3f7; --red:#e05252;
          --text:#d0d0d0; --text2:#999; --mono:'Fira Mono',monospace; }
  * { box-sizing:border-box; margin:0; padding:0; }
  body { background:var(--bg); color:var(--text); font-family:var(--mono);
         font-size:13px; line-height:1.6; padding:24px; }
  h1 { color:var(--cyan); font-size:18px; margin-bottom:4px; }
  .sub { color:var(--text2); font-size:11px; margin-bottom:24px; }
  h2 { color:var(--amber); font-size:12px; text-transform:uppercase;
       letter-spacing:.1em; margin:24px 0 10px; border-bottom:1px solid var(--border);
       padding-bottom:4px; }
  table { width:100%; border-collapse:collapse; margin-bottom:8px; }
  th { text-align:left; color:var(--text2); font-size:10px; text-transform:uppercase;
       padding:4px 8px; border-bottom:1px solid var(--border); }
  td { padding:6px 8px; border-bottom:1px solid var(--border); vertical-align:top; }
  td:first-child { color:var(--green); white-space:nowrap; }
  td:nth-child(2) { color:var(--cyan); white-space:nowrap; }
  .note { background:var(--bg3); border:1px solid var(--border); padding:10px 14px;
          font-size:11px; color:var(--text2); margin-top:20px; }
  .prefix { color:var(--amber); }
</style>
</head>
<body>
<h1>- RigGPT Control Channel Commands</h1>
<p class="sub">Send these in the Discord control channel. All commands start with <span class="prefix">!</span></p>

<h2>- Chaos &amp; Injection</h2>
<table>
<tr><th>Command</th><th>Example</th><th>Effect</th></tr>
<tr><td>!chaos</td><td>!chaos</td><td>Inject a random wildcard event into the current trip immediately</td></tr>
<tr><td>!inject &lt;text&gt;</td><td>!inject A goat walks in wearing a lab coat</td><td>Inject custom chaos text into the debate</td></tr>
<tr><td>!static</td><td>!static</td><td>Insert a STATIC BURST marker - agents react to transmission interference</td></tr>
<tr><td>!oracle</td><td>!oracle</td><td>Toggle ORACLE mode on/off - agents speak only in prophecy and riddles</td></tr>
</table>

<h2>- Persona &amp; Topic</h2>
<table>
<tr><th>Command</th><th>Example</th><th>Effect</th></tr>
<tr><td>!topic &lt;text&gt;</td><td>!topic whether ghosts use WiFi</td><td>Steer the debate toward a new topic mid-trip</td></tr>
<tr><td>!persona a &lt;text&gt;</td><td>!persona a You are now a very tired pirate</td><td>Override Agent A's persona mid-trip</td></tr>
<tr><td>!persona b &lt;text&gt;</td><td>!persona b You are a sentient spreadsheet</td><td>Override Agent B's persona mid-trip</td></tr>
<tr><td>!name a &lt;name&gt;</td><td>!name a BARNACLE</td><td>Rename Agent A on the fly</td></tr>
<tr><td>!name b &lt;name&gt;</td><td>!name b FORMULA_7</td><td>Rename Agent B on the fly</td></tr>
</table>

<h2>- Trip Control</h2>
<table>
<tr><th>Command</th><th>Example</th><th>Effect</th></tr>
<tr><td>!stop</td><td>!stop</td><td>Stop the current trip after this turn</td></tr>
<tr><td>!temp &lt;value&gt;</td><td>!temp 1.6</td><td>Change temperature mid-trip (0.5-2.0)</td></tr>
<tr><td>!paranoid</td><td>!paranoid</td><td>Load the Increasing Paranoia scenario preset</td></tr>
<tr><td>!loop</td><td>!loop</td><td>Load the Memory Loop scenario preset</td></tr>
<tr><td>!decay</td><td>!decay</td><td>Load the Signal Decay scenario preset</td></tr>
</table>

<h2>- Funny / Weird</h2>
<table>
<tr><th>Command</th><th>Example</th><th>Effect</th></tr>
<tr><td>!shush</td><td>!shush</td><td>Injects: "Both agents are struck suddenly silent by something outside the window"</td></tr>
<tr><td>!sneeze</td><td>!sneeze</td><td>Injects: "Agent A sneezes violently. The whole debate pivots."</td></tr>
<tr><td>!lightning</td><td>!lightning</td><td>Injects: "A lightning strike. The lights flicker. When they come back, something is different."</td></tr>
<tr><td>!wrong</td><td>!wrong</td><td>Injects: "Everything one of them just said was completely wrong. The other one knows it."</td></tr>
<tr><td>!alien</td><td>!alien</td><td>Injects: "A third voice briefly joins the transmission. It is not human."</td></tr>
<tr><td>!coffee</td><td>!coffee</td><td>Injects: "Someone has had too much coffee. It shows."</td></tr>
<tr><td>!404</td><td>!404</td><td>Injects: "Agent B has lost the thread entirely and must reconstruct the argument from scratch."</td></tr>
<tr><td>!drama</td><td>!drama</td><td>Injects: "Maximum drama. Something deeply personal has just been revealed."</td></tr>
</table>

<div class="note">
  <strong>Notes:</strong><br>
  - Commands are processed within one poll interval (default 10s) of being posted.<br>
  - If no trip is running, most commands are queued and fire when the next trip starts.<br>
  - !inject, !topic, and !persona accept free-form text of any length.<br>
  - Configure the control channel in RigGPT Config tab under DISCORD CONTROL CHANNEL.
</div>
</body>
</html>"""
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}


# -- System health ---------------------------------------------
@app.route('/api/system/health')
def api_system_health():
    import subprocess as sp, shutil, platform, os
    h = {
        'timestamp':  _now_utc(),
        'platform':   platform.platform(),
        'python':     platform.python_version(),
        'uptime_s':   None, 'cpu_pct': None,
        'ram_total':  None, 'ram_used': None, 'ram_pct': None,
        'disk_total': None, 'disk_used': None, 'disk_pct': None,
        'load_avg':   None, 'processes': {},
        'deps': {}, 'services': {}, 'db_size_kb': None,
        'db_rows': {}, 'log_lines': [],
    }
    if _psutil_ok:
        h['cpu_pct']   = _psutil.cpu_percent(interval=0.4)
        vm = _psutil.virtual_memory()
        h['ram_total'] = round(vm.total/1024**2)
        h['ram_used']  = round(vm.used/1024**2)
        h['ram_pct']   = vm.percent
        du = _psutil.disk_usage('/')
        h['disk_total']= round(du.total/1024**3,1)
        h['disk_used'] = round(du.used/1024**3,1)
        h['disk_pct']  = round(du.used/du.total*100,1)
        try:
            h['load_avg'] = [round(x,2) for x in _psutil.getloadavg()]
        except Exception:
            pass
        try:
            h['uptime_s'] = int(time_module.time()-_psutil.boot_time())
        except Exception:
            pass
        for proc in _psutil.process_iter(['pid','name','cmdline','cpu_percent','memory_percent','status']):
            try:
                cmd = ' '.join(proc.info['cmdline'] or [])
                name = proc.info['name']
                if 'app.py' in cmd:
                    h['processes']['riggpt'] = {
                        'pid':proc.info['pid'], 'cpu':proc.info['cpu_percent'],
                        'mem':round(proc.info['memory_percent'],1), 'status':proc.info['status']}
                elif name in ('nginx','apache2','sshd','mosquitto'):
                    h['processes'][name] = {'pid':proc.info['pid'],'status':proc.info['status']}
            except Exception:
                pass

    dep_checks = {
        'sox':         ['sox','--version'],
        'ffmpeg':      ['ffmpeg','-version'],
        'aplay':       ['aplay','--version'],
        'espeak-ng':   ['espeak-ng','--version'],
        'python3':     ['python3','--version'],
        'pyserial':    ['python3','-c','import serial; print(serial.VERSION)'],
        'flask':       ['python3','-c','import flask; print(flask.__version__)'],
        'apscheduler': ['python3','-c','import apscheduler; print(apscheduler.__version__)'],
        'psutil':      ['python3','-c','import psutil; print(psutil.__version__)'],
        'pysstv':      ['python3','-c','import pysstv; print("ok")'],
        'pillow':      ['python3','-c','from PIL import Image; print(Image.__version__)'],
    }
    for dep, cmd in dep_checks.items():
        try:
            r = sp.run(cmd, capture_output=True, text=True, timeout=5)
            raw = (r.stdout+r.stderr).strip()
            out = raw.splitlines()[0][:60] if raw else 'ok'
            h['deps'][dep] = {'ok': r.returncode==0, 'version': out}
        except Exception as e:
            h['deps'][dep] = {'ok': False, 'version': str(e)[:40]}

    for svc in ['riggpt']:
        try:
            r = sp.run(['systemctl','is-active',svc], capture_output=True, text=True, timeout=3)
            h['services'][svc] = r.stdout.strip()
        except Exception:
            h['services'][svc] = 'unknown'

    try:
        h['db_size_kb'] = round(os.path.getsize(DB_PATH)/1024, 1)
        conn = sqlite3.connect(DB_PATH)
        h['db_rows']['transmissions'] = conn.execute('SELECT COUNT(*) FROM transmissions').fetchone()[0]
        h['db_rows']['system_events'] = conn.execute('SELECT COUNT(*) FROM system_events').fetchone()[0]
        conn.close()
    except Exception:
        pass

    try:
        r = sp.run(['journalctl','-u','riggpt','-n','60',
                    '--no-pager','--output=short'], capture_output=True, text=True, timeout=5)
        h['log_lines'] = r.stdout.strip().splitlines() if r.returncode==0 else []
    except Exception:
        h['log_lines'] = []

    return jsonify(h)





# v2.10.15 -- Trenchtown Dub Studio API
# =============================================================

# =============================================================
# Trenchtown -- ffmpeg effects chain
# =============================================================

def _build_ffmpeg_filters(fx: dict) -> list:
    """Convert Trenchtown fx dict into an ffmpeg -af filter chain.
    Every filter here has been validated against ffmpeg 6.1 on this system."""
    filters = []

    # -- Dynamics ------------------------------------------------
    vol = float(fx.get('volume', fx.get('vol', 100))) / 100.0
    if vol != 1.0:
        filters.append(f'volume={vol:.3f}')

    compress = float(fx.get('compress', 0))
    if compress > 0:
        ratio = 1.0 + (compress / 100.0) * 9.0        # 1:1 - 10:1
        filters.append(
            f'acompressor=threshold=0.1:ratio={ratio:.1f}:attack=0.2:release=0.3'
        )

    gate = float(fx.get('gate', 0))
    if gate > 0:
        threshold = -(gate / 100.0) * 40              # 0-100 - 0 to -40 dB
        filters.append(f'agate=threshold={threshold:.1f}dB:ratio=10')

    # -- Tone / Filter --------------------------------------------
    hpf = int(fx.get('hpf', 0))
    if hpf > 0:
        filters.append(f'highpass=f={hpf}')

    lpf = int(fx.get('lpf', 20000))
    if lpf < 20000:
        filters.append(f'lowpass=f={lpf}')

    # -- Bass / Treble EQ shelves ---------------------------------
    bass = float(fx.get('bass', 0))
    if bass != 0:
        # bass_boost shelves below 200 Hz - positive boosts, negative cuts
        g = max(-20.0, min(20.0, bass))
        filters.append(f'bass=g={g:.1f}:f=200:width_type=o:width=2')

    treble = float(fx.get('treble', 0))
    if treble != 0:
        g = max(-20.0, min(20.0, treble))
        filters.append(f'treble=g={g:.1f}:f=3000:width_type=o:width=2')

    # -- Mid EQ (presence/body control around 1.5kHz) ------------
    mid = float(fx.get('mid', 0))
    if mid != 0:
        g = max(-20.0, min(20.0, mid))
        filters.append(f'equalizer=f=1500:t=o:w=2:g={g:.1f}')

    # -- Pitch (preserves tempo via counter-atempo) ---------------
    pitch = float(fx.get('pitch', 0))
    if pitch != 0:
        ratio = 2 ** (pitch / 12.0)
        # Counteract the speed change so only pitch is shifted
        inv = 1.0 / ratio
        inv = max(0.5, min(2.0, inv))                  # atempo range clamp
        filters.append(
            f'asetrate=44100*{ratio:.6f},aresample=44100,atempo={inv:.6f}'
        )

    # -- Speed / Tempo (no pitch change) -------------------------
    speed = float(fx.get('speed', 1.0))
    if abs(speed - 1.0) > 0.01:
        speed = max(0.25, min(4.0, speed))
        if speed < 0.5:
            filters.append(f'atempo=0.5,atempo={speed/0.5:.4f}')
        elif speed > 2.0:
            filters.append(f'atempo=2.0,atempo={speed/2.0:.4f}')
        else:
            filters.append(f'atempo={speed:.4f}')

    # -- Distortion: volume boost - alimiter hard clip ------------
    dist = float(fx.get('overdrive', fx.get('dist', 0)))
    if dist > 0:
        gain = 1.0 + (dist / 100.0) * 19.0            # 1- - 20- boost
        filters.append(f'volume={gain:.2f},alimiter=limit=0.95')
        filters.append('volume=0.7')                   # compensate loudness

    # -- Bitcrush via acrusher ------------------------------------
    bits = int(fx.get('bitcrush', 0))
    if bits > 0:
        effective = max(1, 15 - bits)                  # 0-15bit, 14-1bit
        filters.append(f'acrusher=bits={effective}:mode=lin:aa=1')

    # -- Stutter (volume-chop into repeating slices via tremolo) --
    stutter = float(fx.get('stutter', 0))
    if stutter > 0:
        # Map 0-100 to tremolo frequency 4-20 Hz and full depth
        stutter_freq = 4.0 + (stutter / 100.0) * 16.0
        filters.append(f'tremolo=f={stutter_freq:.1f}:d=1.0')
        # Add a short echo to enhance the stutter effect
        stutter_delay = max(20, int(300 - stutter * 2.8))
        filters.append(f'aecho=0.8:0.7:{stutter_delay}:0.5')

    # -- Stereo Width (haas/pan widening) ------------------------
    width = float(fx.get('width', 100))
    if abs(width - 100) > 2:
        if width == 0:
            # Fold to mono
            filters.append('pan=mono|c0=0.5*c0+0.5*c1')
            filters.append('aformat=channel_layouts=stereo')
        elif width < 100:
            # Narrow: blend channels toward mono
            m = (100 - width) / 100.0 * 0.5
            s = 1.0 - m
            filters.append(f'stereotools=mwidth={s:.3f}:mlevel=1')
        else:
            # Wide: use Haas effect (small delay on one channel for apparent width)
            haas_ms = min(40, int((width - 100) / 100.0 * 40))
            if haas_ms > 0:
                filters.append(f'stereotools=mwidth=1.5:mlevel=0.8')

    # -- Modulation -----------------------------------------------
    chorus = float(fx.get('chorus', 0))
    if chorus > 0:
        d  = chorus / 100.0 * 0.04 + 0.005            # depth 0.005-0.045
        sp = 0.25 + chorus / 100.0 * 0.5              # speed 0.25-0.75 Hz
        filters.append(
            f'chorus=0.7:0.9:{int(45+chorus)}|{int(60+chorus*0.7)}'
            f':{d:.3f}|{d*0.75:.3f}:{sp:.3f}|{sp*0.8:.3f}:2|2.3'
        )

    flanger = float(fx.get('flanger', 0))
    if flanger > 0:
        depth = flanger / 100.0 * 10.0                # 0-10 (ffmpeg max)
        filters.append(
            f'flanger=delay=5:depth={depth:.1f}:regen=0:width=71'
            f':speed=0.5:shape=sinusoidal:phase=25:interp=linear'
        )

    phaser = float(fx.get('phaser', 0))
    if phaser > 0:
        decay = 0.2 + phaser / 100.0 * 0.6
        speed = 0.3 + phaser / 100.0 * 1.0
        filters.append(
            f'aphaser=in_gain=0.4:out_gain=0.74:delay=3'
            f':decay={decay:.2f}:speed={speed:.2f}:type=t'
        )

    tremolo = float(fx.get('tremolo', 0))
    if tremolo > 0:
        freq  = 2.0 + tremolo / 100.0 * 8.0           # 2-10 Hz
        depth = tremolo / 100.0 * 0.9 + 0.1           # 0.1-1.0
        filters.append(f'tremolo=f={freq:.1f}:d={depth:.2f}')

    vibrato = float(fx.get('vibrato', 0))
    if vibrato > 0:
        freq  = 3.0 + vibrato / 100.0 * 7.0           # 3-10 Hz
        depth = vibrato / 100.0 * 0.9 + 0.05
        filters.append(f'vibrato=f={freq:.1f}:d={depth:.2f}')

    # -- Space (echo/reverb) --------------------------------------
    echo = int(fx.get('echo', 0))
    if echo > 0:
        # echo_fb: 0-90 maps to feedback decay 0.1-0.85
        fb_pct = float(fx.get('echo_fb', 40))
        decay  = 0.1 + (fb_pct / 90.0) * 0.75
        decay  = min(0.85, max(0.1, decay))
        filters.append(f'aecho=0.8:{decay:.2f}:{echo}:{decay*0.55:.2f}')

    reverb = float(fx.get('reverb', 0))
    if reverb > 0:
        r = reverb / 100.0
        d1,d2,d3,d4 = int(20+r*30), int(35+r*55), int(55+r*90), int(85+r*140)
        c1,c2,c3,c4 = r*0.42, r*0.36, r*0.26, r*0.18
        filters.append(
            f'aecho=0.8:0.9:{d1}|{d2}|{d3}|{d4}:{c1:.2f}|{c2:.2f}|{c3:.2f}|{c4:.2f}'
        )

    # -- Final loudnorm -------------------------------------------
    if fx.get('normalize', False):
        filters.append('loudnorm=I=-20:TP=-2:LRA=11')

    return filters


def _apply_trenchtown_fx(in_wav: str, out_wav: str, fx: dict) -> bool:
    """Run ffmpeg effects chain. Returns True on success."""
    filters = _build_ffmpeg_filters(fx)
    wet = float(fx.get('wet', 100)) / 100.0
    wet = max(0.0, min(1.0, wet))

    if not filters and wet >= 0.99:
        # No effects, full wet - just copy
        import shutil
        shutil.copy2(in_wav, out_wav)
        return True

    if not filters:
        # No FX but wet < 1.0 -- treat as a volume fade toward dry
        af = f'volume={wet:.3f}'
        cmd = ['ffmpeg', '-y', '-i', in_wav, '-af', af, out_wav]
    elif wet >= 0.99:
        # Full wet - normal path
        af = ','.join(filters)
        cmd = ['ffmpeg', '-y', '-i', in_wav, '-af', af, out_wav]
    else:
        # Parallel dry/wet mix using amix + asplit
        dry = 1.0 - wet
        af_wet = ','.join(filters)
        af = (
            f'asplit=2[dry][wet_in];'
            f'[wet_in]{af_wet}[wet_out];'
            f'[dry]volume={dry:.3f}[d];'
            f'[wet_out]volume={wet:.3f}[w];'
            f'[d][w]amix=inputs=2:normalize=0'
        )
        cmd = ['ffmpeg', '-y', '-i', in_wav, '-filter_complex', af, out_wav]
    logger.debug(f'Trenchtown ffmpeg: {" ".join(cmd)}')
    try:
        r = subprocess.run(cmd, capture_output=True, timeout=120)
        if r.returncode != 0:
            logger.error(f'Trenchtown ffmpeg error: {r.stderr.decode()[:400]}')
            return False
        return True
    except Exception as e:
        logger.error(f'Trenchtown ffmpeg exception: {e}')
        return False


@app.route('/api/radio/profiles', methods=['GET'])
def api_radio_profiles():
    """Return RADIO_PROFILES dict for the UI selector."""
    safe = {k: {ek: ev for ek, ev in v.items() if ek != 'audio_hints'}
            for k, v in RADIO_PROFILES.items()}
    return jsonify({'success': True, 'profiles': safe})


# -- Memory / Qdrant routes ---------------------------------------------
@app.route('/api/memory/status', methods=['GET'])
def api_memory_status():
    """Return Qdrant connection state and collection stats."""
    mem = _get_memory()
    return jsonify(mem.status_dict())


@app.route('/api/memory/query', methods=['POST'])
def api_memory_query():
    """Debug endpoint: semantic search against the memory store.
    Body: {query: str, collection: 'discord_messages'|'user_profiles'|'channel_themes', limit: int}
    """
    data  = request.json or {}
    query = _ascii(str(data.get('query', ''))).strip()
    col   = data.get('collection', 'discord_messages')
    limit = max(1, min(20, int(data.get('limit', 5))))
    if not query:
        return jsonify({'success': False, 'message': 'query required'}), 400
    mem     = _get_memory()
    if not mem.is_available():
        return jsonify({'success': False, 'message': 'Memory not available'}), 503
    try:
        if col == 'channel_themes':
            results = [mem.get_channel_themes()] if mem.get_channel_themes() else []
        elif col == 'user_profiles':
            results = mem.search_profiles(query, limit=limit)
        elif col == 'conversation_threads':
            results = mem.search_threads(query, limit=limit)
        elif col == 'briefing':
            briefing = mem.build_briefing(query)
            results  = [{'briefing': briefing}] if briefing else []
        else:
            results = mem.search_messages(query, limit=limit)
        return jsonify({'success': True, 'results': results, 'count': len(results)})
    except Exception as e:
        return jsonify({'success': False, 'message': _ascii(str(e))}), 500


@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/radio/docs')
def radio_docs_page():
    """Radio model configuration reference page."""
    rows = ''
    for model_id, p in RADIO_PROFILES.items():
        rows += f"""
        <tr>
          <td>{p['label']}</td>
          <td>{p['ci_v_address']}</td>
          <td>{p['baud_rate']}</td>
          <td>{p['udev_hint']}</td>
          <td>{p['notes']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>RigGPT - Radio Configuration</title>
<style>
  :root {{ --bg:#0d0d0d; --bg2:#141414; --bg3:#1a1a1a; --border:#2a2a2a;
           --green:#39d353; --amber:#e8a020; --cyan:#4fc3f7; --red:#e05252;
           --text:#d0d0d0; --text2:#999; --text3:#666; --mono:'Fira Mono',monospace; }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  body {{ background:var(--bg); color:var(--text); font-family:var(--mono);
          font-size:13px; line-height:1.6; padding:28px 32px; max-width:1000px; }}
  h1 {{ color:var(--cyan); font-size:20px; margin-bottom:4px; }}
  .sub {{ color:var(--text3); font-size:11px; margin-bottom:28px; }}
  h2 {{ color:var(--amber); font-size:12px; text-transform:uppercase;
        letter-spacing:.1em; margin:28px 0 10px; border-bottom:1px solid var(--border);
        padding-bottom:4px; }}
  p {{ margin-bottom:10px; color:var(--text2); }}
  table {{ width:100%; border-collapse:collapse; margin-bottom:12px; font-size:12px; }}
  th {{ text-align:left; color:var(--text3); font-size:10px; text-transform:uppercase;
        padding:5px 10px; border-bottom:1px solid var(--border); }}
  td {{ padding:7px 10px; border-bottom:1px solid var(--border); vertical-align:top; }}
  tr:first-child td {{ color:var(--green); }}
  td:nth-child(2) {{ color:var(--cyan); white-space:nowrap; }}
  td:nth-child(3) {{ color:var(--amber); white-space:nowrap; }}
  td:nth-child(4) {{ color:var(--text3); white-space:nowrap; font-size:11px; }}
  code {{ background:var(--bg3); border:1px solid var(--border); padding:1px 5px;
          font-family:var(--mono); font-size:12px; color:var(--amber); }}
  .box {{ background:var(--bg2); border:1px solid var(--border); padding:14px 18px;
          margin:12px 0; font-size:12px; }}
  .box h3 {{ color:var(--green); margin-bottom:8px; font-size:12px; }}
  .warn {{ border-color:var(--amber); }}
  .warn h3 {{ color:var(--amber); }}
  .step {{ counter-increment:step; }}
  ol {{ counter-reset:step; list-style:none; padding:0; }}
  ol li::before {{ content:counter(step)'.'; color:var(--cyan); margin-right:8px; font-weight:bold; }}
  ol li {{ margin-bottom:6px; color:var(--text2); }}
  .radio-note {{ color:var(--text3); font-size:11px; }}
</style>
</head>
<body>
<h1>- RigGPT Radio Configuration</h1>
<p class="sub">Connection reference for supported Icom transceivers &mdash; v{VERSION}</p>

<h2>Supported Radio Models</h2>
<p>Select your radio in the RigGPT Dashboard (Connection panel &rarr; RADIO MODEL dropdown).
   This pre-fills the CI-V address and baud rate. The IC-7610 is the default and no changes
   are required if that is your radio.</p>
<table>
<tr>
  <th>Radio</th><th>CI-V Address</th><th>Baud Rate</th>
  <th>udev Symlink Hint</th><th>Notes</th>
</tr>
{rows}
</table>

<h2>Step 1 &mdash; USB Serial (CI-V) Port</h2>
<p>RigGPT controls the radio via the CI-V protocol over USB. Each radio model presents a different
   USB serial device to the OS. The recommended approach is a persistent udev symlink so the device
   path never changes between reboots or cable replugs.</p>

<div class="box">
<h3>Create a persistent udev symlink (recommended)</h3>
<ol>
<li>Find the radio's USB vendor/product IDs:<br>
    <code>lsusb</code> while the radio is connected &mdash; look for Silicon Labs CP210x or FTDI entries.</li>
<li>Find the serial number (use <code>udevadm info /dev/ttyUSB0</code> or similar to identify the correct port).</li>
<li>Create <code>/etc/udev/rules.d/99-riggpt.rules</code>:<br>
    <code>SUBSYSTEM=="tty", ATTRS{{idVendor}}=="10c4", ATTRS{{idProduct}}=="ea60", ATTRS{{serial}}=="YOUR_SERIAL", SYMLINK+="ttyIC7610"</code></li>
<li>Reload udev: <code>sudo udevadm control --reload-rules &amp;&amp; sudo udevadm trigger</code></li>
<li>Verify: <code>ls -la /dev/ttyIC7610</code></li>
</ol>
</div>

<div class="box warn">
<h3>Common USB serial IDs by radio</h3>
<p><strong>IC-7610, IC-7300, IC-9700</strong> &mdash; Silicon Labs CP2102: <code>idVendor=10c4 idProduct=ea60</code></p>
<p><strong>IC-7410, IC-7100</strong> &mdash; Silicon Labs CP210x: <code>idVendor=10c4 idProduct=ea60</code> (same chip, differentiate by serial number)</p>
<p>If you only have one Icom radio, the serial number step is optional &mdash; just match vendor/product.</p>
</div>

<h2>Step 2 &mdash; CI-V Address</h2>
<p>The CI-V address must match what is set in the radio's menu. Factory defaults are listed in the
   table above. To verify or change the address on the radio:</p>
<div class="box">
<h3>Reading / setting CI-V address on IC-7610</h3>
<ol>
<li>Press <code>MENU</code></li>
<li>Navigate to <code>SET &rarr; Connectors &rarr; CI-V &rarr; CI-V Address</code></li>
<li>Factory default is <code>98h</code></li>
<li>The address in RigGPT must match (enter as <code>0x98</code> or <code>0X98</code>)</li>
</ol>
</div>
<div class="box">
<h3>Reading / setting CI-V address on IC-7410</h3>
<ol>
<li>Press <code>MENU</code></li>
<li>Navigate to <code>SET &rarr; Connectors &rarr; CI-V Baud Rate</code> and <code>CI-V Address</code></li>
<li>Factory default is <code>6Eh</code></li>
<li>Set baud rate to match RigGPT (19200 default for 7410)</li>
</ol>
</div>
<div class="box">
<h3>Reading / setting CI-V address on IC-7300</h3>
<ol>
<li>Press <code>MENU</code></li>
<li>Navigate to <code>SET &rarr; Connectors &rarr; CI-V &rarr; CI-V Address</code></li>
<li>Factory default is <code>94h</code></li>
<li>IC-7300 supports up to 115200 baud &mdash; recommended for lowest latency</li>
</ol>
</div>

<h2>Step 3 &mdash; USB Audio</h2>
<p>RigGPT synthesizes speech and plays it into the radio's USB audio input. All listed radios
   have a built-in USB sound card. RigGPT auto-detects the correct audio device on startup
   by scanning <code>aplay -l</code> output for known chip identifiers.</p>
<div class="box">
<h3>If auto-detection picks the wrong device</h3>
<ol>
<li>Run <code>aplay -l</code> and find the correct card number for your radio.</li>
<li>Set the environment variable before starting RigGPT:<br>
    <code>RIGGPT_AUDIO_DEVICE=hw:2,0 python app.py</code></li>
<li>Or add it to your systemd service file under <code>[Service]</code>:<br>
    <code>Environment=RIGGPT_AUDIO_DEVICE=hw:2,0</code></li>
<li>The health panel in the Config tab shows the currently detected audio device.</li>
</ol>
</div>
<div class="box warn">
<h3>Audio levels</h3>
<p>TX audio level is set in the radio menu, not in software. Start with the radio's
   USB AF Level at 50% and ALC at the standard position. Drive the audio until the
   ALC meter barely moves &mdash; this gives the cleanest signal.</p>
<p>For SSB voice modes (USB/LSB), the radio modulates the audio. For digital modes
   or SSTV, disable internal compression and use a flat audio response.</p>
</div>

<h2>Running Multiple Radios</h2>
<p>RigGPT supports one active radio connection at a time. To switch radios: disconnect,
   select the new radio model from the dropdown (which pre-fills CI-V address and baud rate),
   update the serial port if needed, and reconnect.</p>
<p>If you use two radios regularly, consider two separate RigGPT installations on different ports,
   or two systemd service instances with different <code>RIGGPT_AUDIO_DEVICE</code> and port settings.</p>

<h2>Troubleshooting</h2>
<div class="box">
<h3>No CI-V response / timeout</h3>
<ol>
<li>Verify the serial port is correct: <code>ls /dev/tty*</code></li>
<li>Check that the RigGPT user has serial port access: <code>sudo usermod -aG dialout riggpt</code></li>
<li>Confirm CI-V address and baud rate match the radio menu exactly.</li>
<li>Try the PTT Test button in RigGPT &mdash; if PTT keys but freq readout fails, it is likely a CI-V address mismatch.</li>
<li>On IC-7610 / IC-7300 / IC-9700: ensure <code>CI-V USB &rarr; Unlink from [REMOTE]</code> is set if using USB control.</li>
</ol>
</div>
<div class="box">
<h3>Audio transmits but sounds wrong</h3>
<ol>
<li>Confirm the radio is in SSB mode (USB recommended for voice). AM/FM mode will not work well with synthesized voice.</li>
<li>Run a PTT test in RigGPT and monitor your own transmission on a second receiver.</li>
<li>If audio is distorted, lower the USB AF Level in the radio menu.</li>
<li>If audio is too quiet, increase USB AF Level or check that the correct audio card is selected.</li>
</ol>
</div>

</body>
</html>"""
    return html, 200, {'Content-Type': 'text/html; charset=utf-8'}



@app.route('/api/canon/list')
def api_canon_list():
    """Return sorted list of .md filenames in canon/a and canon/b directories."""
    import os
    result = {}
    for agent, d in [('a', CANON_DIR_A), ('b', CANON_DIR_B)]:
        try:
            os.makedirs(d, exist_ok=True)
            files = sorted(
                f for f in os.listdir(d)
                if f.lower().endswith('.md') and os.path.isfile(os.path.join(d, f))
            )
        except Exception as e:
            files = []
            app.logger.warning('canon list %s: %s', d, e)
        result[agent] = files
    return jsonify({'success': True, 'files': result})


@app.route('/api/canon/file')
def api_canon_file():
    """Return contents of a canon .md file for a given agent."""
    import os
    agent = request.args.get('agent', '').lower().strip()
    name  = request.args.get('name', '').strip()
    if agent not in ('a', 'b'):
        return jsonify({'success': False, 'message': 'agent must be a or b'}), 400
    if not name or not name.lower().endswith('.md') or '/' in name or '..' in name:
        return jsonify({'success': False, 'message': 'invalid filename'}), 400
    d    = CANON_DIR_A if agent == 'a' else CANON_DIR_B
    path = os.path.join(d, name)
    if not os.path.isfile(path):
        return jsonify({'success': False, 'message': 'file not found'}), 404
    try:
        text = open(path, 'r', encoding='utf-8').read()
        return jsonify({'success': True, 'content': text, 'name': name})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500




@app.route('/api/trenchtown/transmit', methods=['POST'])
def api_trenchtown_transmit():
    """Apply ffmpeg effects chain to WAV or TTS text, then transmit over PTT."""
    import base64
    data    = request.json or {}
    wav_b64 = data.get('wav_b64', '')
    text    = data.get('text', '').strip()
    engine  = data.get('engine', 'espeak')
    fx      = data.get('effects', {})
    dry_run = data.get('dry_run', False)

    if not wav_b64 and not text:
        return jsonify({'success': False, 'message': 'No audio source (wav_b64 or text required)'}), 400

    # -- Serialise live TX: only one PTT transmission at a time --
    # Preview (dry_run) requests are cheap and can run concurrently.
    # Live TX holds the lock for the duration of PTT + playback.
    if not dry_run:
        acquired = _trenchtown_lock.acquire(blocking=False)
        if not acquired:
            logger.warning('Trenchtown: TX busy - dropping duplicate request')
            return jsonify({'success': False,
                            'message': 'TX busy - previous transmission still in progress',
                            'busy': True}), 409

    _fd, in_wav  = tempfile.mkstemp(suffix='_dub_in.wav')
    os.close(_fd)
    _fd, out_wav = tempfile.mkstemp(suffix='_dub_out.wav')
    os.close(_fd)
    ptt_active = False

    try:
        # --- Source ---
        if wav_b64:
            raw = base64.b64decode(wav_b64)
            with open(in_wav, 'wb') as f: f.write(raw)
        else:
            # Synthesize TTS to in_wav via inline dispatch
            # Dispatch to appropriate TTS agent
            if engine == 'elevenlabs':
                voice = data.get('voice') or None
                result = ElevenLabsTTSAgent().synthesize(text, voice_id=voice, output_path=in_wav)
            elif engine == 'speechify':
                voice = data.get('voice') or None
                result = SpeechifyTTSAgent().synthesize(text, voice=voice, output_path=in_wav)
            elif engine == 'piper':
                voice = data.get('voice') or None
                result = PiperTTSAgent().synthesize(text, voice=voice, output_path=in_wav)
            elif engine == 'edge':
                voice = data.get('voice') or None
                result = EdgeTTSAgent().synthesize(text, voice=voice, output_path=in_wav)
            elif engine == 'gtts':
                voice = data.get('voice') or None
                result = GTTSAgent().synthesize(text, voice=voice, output_path=in_wav)
            elif engine == 'espeak':
                voice = data.get('voice') or 'en-us'
                result = EspeakTTSAgent().synthesize(text, voice=voice, output_path=in_wav)
            elif engine == 'openai':
                # OpenAI TTS uses the orchestrator's approach - delegate to transmit pipeline
                voice = data.get('voice') or 'alloy'
                try:
                    import openai as _oai
                    from api_keys import get_key as _gk
                    _oa_key = _gk('openai', 'api_key') or os.environ.get('OPENAI_API_KEY','')
                    if not _oa_key:
                        return jsonify({'success': False, 'message': 'OpenAI API key not configured'}), 400
                    _oai.api_key = _oa_key
                    resp = _oai.audio.speech.create(model='tts-1', voice=voice, input=text, response_format='wav')
                    resp.stream_to_file(in_wav)
                    result = in_wav
                except Exception as _oe:
                    return jsonify({'success': False, 'message': f'OpenAI TTS error: {_oe}'}), 500
            else:
                result = EspeakTTSAgent().synthesize(text, output_path=in_wav)
            if not result or not os.path.exists(in_wav) or os.path.getsize(in_wav) == 0:
                return jsonify({'success': False, 'message': 'TTS synthesis failed'}), 500

        # --- Effects chain ---
        if not _apply_trenchtown_fx(in_wav, out_wav, fx):
            return jsonify({'success': False, 'message': 'ffmpeg effects processing failed'}), 500

        if dry_run:
            # Return processed audio as base64 for preview
            with open(out_wav, 'rb') as f:
                result_b64 = base64.b64encode(f.read()).decode('ascii')
            size_kb = round(os.path.getsize(out_wav) / 1024, 1)
            return jsonify({'success': True, 'message': f'Preview ready ({size_kb}KB)',
                            'preview_b64': result_b64, 'size_kb': size_kb})

        # --- Transmit ---
        log_event('INFO', 'TRENCHTOWN', f'Transmitting {os.path.getsize(out_wav)//1024}KB processed audio')
        try:
            global _poller_paused
            _poller_paused = True   # keep radio poller off the serial bus during PTT
            orchestrator.icom_agent.ptt_on()
            ptt_active = True
            time_module.sleep(0.3)
            orchestrator.playback_agent.play(out_wav, normalize=False)
            time_module.sleep(0.2)
            orchestrator.icom_agent.ptt_off()
            ptt_active = False
            success = True
        except Exception as ptt_err:
            logger.error(f'Trenchtown PTT error: {ptt_err}')
            success = False
        finally:
            _poller_paused = False  # always resume poller

        log_transmission('Trenchtown dub transmission', 'trenchtown', engine, '',
                         data.get('duration', 0), success, notes=str(fx))
        return jsonify({'success': success,
                        'message': 'Transmitted!' if success else 'PTT failed'})

    except Exception as e:
        logger.error(f'Trenchtown error: {e}')
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        if ptt_active:
            try: orchestrator.icom_agent.ptt_off()
            except Exception: pass
        for f in [in_wav, out_wav]:
            try:
                if os.path.exists(f): os.remove(f)
            except Exception: pass
        # Release TX lock (only held for live TX, not dry_run)
        if not dry_run and _trenchtown_lock.locked():
            try: _trenchtown_lock.release()
            except RuntimeError: pass




# =============================================================
# Startup -- runs under both gunicorn and direct python3 app.py
# =============================================================

def _auto_connect():
    """Try serial ports in scored order and connect to the first responding radio."""
    scored = IcomSerialAgent.score_ports()
    candidates = [SERIAL_PORT]
    for p in scored:
        if p['device'] not in candidates:
            candidates.append(p['device'])
    for port in candidates:
        if not os.path.exists(port):
            continue
        logger.info(f"Auto-connect: trying {port}...")
        if orchestrator.connect(port):
            logger.info(f"Auto-connect: port opened {port} @ {orchestrator.icom_agent.baudrate} -- radio probe deferred to poller")
            return  # poller thread will do full probe and baud-scan without blocking startup
    logger.warning("Auto-connect: no serial port found -- connect manually via Settings tab")


# =============================================================
# SPECIAL OPS — Numbers Station, Solar Weather, Mystery TX, Auto-ID
# =============================================================

# ── Numbers Station ───────────────────────────────────────────────────────
def _run_numbers_station():
    """Transmit a Cold War-style numbers group over the air."""
    import random
    groups = '  '.join(
        ' '.join(str(random.randint(0, 9)) for _ in range(5))
        for _ in range(5)
    )
    intro = random.choice(['ATTENTION', 'STAND BY', 'THIS IS', 'RELAY RELAY', 'OSCAR LIMA'])
    msg   = f'{intro}.  {groups}.  END TRANSMISSION.'
    engine = _app_settings.get('numbers_station_engine', 'espeak')
    try:
        orchestrator.execute(msg, engine=engine, voice='en-us', preset='normal', roger_beep=False)
        logger.info(f'numbers_station: transmitted {len(groups.split())} groups')
    except Exception as e:
        logger.error(f'numbers_station TX error: {e}')


@app.route('/api/numbers_station/start', methods=['POST'])
def api_numbers_station_start():
    global _numbers_station_job
    if not scheduler:
        return jsonify({'success': False, 'message': 'Scheduler not available'}), 503
    data     = request.json or {}
    interval = max(1, int(data.get('interval_minutes',
                          int(_app_settings.get('numbers_station_interval', 5)))))
    engine   = data.get('engine', _app_settings.get('numbers_station_engine', 'espeak'))
    _app_settings['numbers_station_interval'] = str(interval)
    _app_settings['numbers_station_engine']   = engine
    _save_app_settings(_app_settings)
    try:
        if _numbers_station_job:
            try: _numbers_station_job.remove()
            except Exception: pass
        _numbers_station_job = scheduler.add_job(
            _run_numbers_station,
            CronTrigger.from_crontab(f'*/{interval} * * * *'),
            id='numbers_station', replace_existing=True,
        )
        threading.Thread(target=_run_numbers_station, daemon=True, name='ns-initial').start()
        return jsonify({'success': True,
                        'message': f'Numbers station active every {interval}min (engine={engine})'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/numbers_station/stop', methods=['POST'])
def api_numbers_station_stop():
    global _numbers_station_job
    if _numbers_station_job:
        try: _numbers_station_job.remove()
        except Exception: pass
        _numbers_station_job = None
    return jsonify({'success': True, 'message': 'Numbers station stopped'})


@app.route('/api/numbers_station/status', methods=['GET'])
def api_numbers_station_status():
    return jsonify({
        'active':   _numbers_station_job is not None,
        'interval': _app_settings.get('numbers_station_interval', '5'),
        'engine':   _app_settings.get('numbers_station_engine', 'espeak'),
    })


# ── Solar Weather ──────────────────────────────────────────────────────────
def _solar_fetch_kindex():
    """Fetch current planetary K-index from NOAA SWPC. Returns float or None."""
    import urllib.request
    try:
        url = 'https://services.swpc.noaa.gov/json/planetary_k_index_1m.json'
        with urllib.request.urlopen(url, timeout=10) as resp:
            rows = json.loads(resp.read())
        if rows:
            return float(rows[-1][1])
    except Exception as e:
        logger.warning(f'solar: K-index fetch error: {e}')
    return None


def _solar_poll_and_announce():
    """Fetch K-index and optionally auto-transmit an alert."""
    k = _solar_fetch_kindex()
    if k is None:
        return
    _solar_cache['k']       = k
    _solar_cache['updated'] = _now_utc()
    threshold = float(_app_settings.get('solar_kindex_threshold', '5'))
    autotx    = _app_settings.get('solar_autotx_enabled', 'false') == 'true'
    if not autotx or k < threshold:
        return
    # Rate-limit: one announcement per 30-minute window
    last = _solar_cache.get('last_announced')
    if last:
        try:
            from datetime import timedelta
            last_dt = datetime.fromisoformat(last.replace('Z', '+00:00'))
            if (datetime.now(timezone.utc) - last_dt).total_seconds() < 1800:
                return
        except Exception:
            pass
    cond_map = {8: 'EXTREME', 7: 'SEVERE', 6: 'STRONG', 5: 'MODERATE'}
    cond = next((v for thr, v in sorted(cond_map.items(), reverse=True) if k >= thr), 'ACTIVE')
    msg = (
        f'ATTENTION ALL STATIONS.  GEOMAGNETIC STORM ALERT.  '
        f'K INDEX IS NOW {k:.0f}.  CONDITION: {cond}.  '
        f'PROPAGATION DISRUPTION POSSIBLE ON HIGHER BANDS.  '
        f'THIS IS AN AUTOMATED ALERT.'
    )
    _solar_cache['last_announced'] = _now_utc()
    try:
        orchestrator.execute(msg, engine='espeak', voice='en-us', preset='normal', roger_beep=False)
        logger.info(f'solar: K={k} alert transmitted (condition={cond})')
    except Exception as e:
        logger.error(f'solar: TX error: {e}')


@app.route('/api/solar/status', methods=['GET'])
def api_solar_status():
    # Always fetch fresh on demand
    k = _solar_fetch_kindex()
    if k is not None:
        _solar_cache['k']       = k
        _solar_cache['updated'] = _now_utc()
    return jsonify({
        'k_index':       _solar_cache.get('k'),
        'updated':       _solar_cache.get('updated'),
        'last_announced': _solar_cache.get('last_announced'),
        'autotx_enabled': _app_settings.get('solar_autotx_enabled', 'false') == 'true',
        'threshold':      float(_app_settings.get('solar_kindex_threshold', '5')),
    })


@app.route('/api/solar/announce', methods=['POST'])
def api_solar_announce():
    """Force an immediate solar weather announcement."""
    _solar_cache['last_announced'] = None  # bypass rate limit
    threading.Thread(target=_solar_poll_and_announce, daemon=True, name='solar-force').start()
    return jsonify({'success': True, 'message': 'Solar weather announcement queued'})


# ── Mystery Transmission ───────────────────────────────────────────────
_MYSTERY_LINES = [
    'The frequency is clear.',
    'We are watching.',
    'Signal lost.  Signal found.',
    'This message will not repeat.',
    'Hello darkness.',
    'You are not alone on this frequency.',
    'The numbers do not lie.',
    'Stand by for further instructions.',
    'All stations.  All stations.  Silence please.',
    'This is not a test.',
]


def _run_mystery_tx():
    import random
    with _clips_lock:
        files = list(_clips_files)
    if files:
        clip = random.choice(files)
        logger.info(f'mystery: transmitting clip: {clip["name"]}')
        threading.Thread(target=_clips_play, args=(clip,), daemon=True, name='mystery-tx').start()
    else:
        msg = random.choice(_MYSTERY_LINES)
        logger.info(f'mystery: transmitting line: {msg!r}')
        try:
            orchestrator.execute(msg, engine='espeak', voice='en-us', preset='cave', roger_beep=False)
        except Exception as e:
            logger.error(f'mystery TX error: {e}')


@app.route('/api/mystery/schedule', methods=['POST'])
def api_mystery_schedule():
    global _mystery_job
    if not scheduler:
        return jsonify({'success': False, 'message': 'Scheduler not available'}), 503
    import random
    data         = request.json or {}
    window_start = int(data.get('window_start_hour',
                        int(_app_settings.get('mystery_window_start', 2))))
    window_end   = int(data.get('window_end_hour',
                        int(_app_settings.get('mystery_window_end', 4))))
    window_end   = max(window_end, window_start + 1)
    _app_settings['mystery_window_start'] = str(window_start)
    _app_settings['mystery_window_end']   = str(window_end)
    _save_app_settings(_app_settings)
    hour   = random.randint(window_start, window_end - 1)
    minute = random.randint(0, 59)
    cron   = f'{minute} {hour} * * *'
    try:
        if _mystery_job:
            try: _mystery_job.remove()
            except Exception: pass
        _mystery_job = scheduler.add_job(
            _run_mystery_tx,
            CronTrigger.from_crontab(cron),
            id='mystery_tx', replace_existing=True,
        )
        return jsonify({'success': True,
                        'message': f'Mystery TX scheduled for {hour:02d}:{minute:02d}',
                        'scheduled_for': f'{hour:02d}:{minute:02d}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/mystery/stop', methods=['POST'])
def api_mystery_stop():
    global _mystery_job
    if _mystery_job:
        try: _mystery_job.remove()
        except Exception: pass
        _mystery_job = None
    return jsonify({'success': True})


@app.route('/api/mystery/fire', methods=['POST'])
def api_mystery_fire():
    threading.Thread(target=_run_mystery_tx, daemon=True, name='mystery-force').start()
    return jsonify({'success': True, 'message': 'Mystery transmission fired'})


@app.route('/api/mystery/status', methods=['GET'])
def api_mystery_status():
    return jsonify({
        'active':       _mystery_job is not None,
        'window_start': _app_settings.get('mystery_window_start', '2'),
        'window_end':   _app_settings.get('mystery_window_end',   '4'),
    })


# ── Auto-ID ───────────────────────────────────────────────────────────────────
def _run_autoid():
    callsign = _app_settings.get('autoid_callsign', '').strip().upper()
    if not callsign:
        logger.warning('auto-id: no callsign configured')
        return
    engine = _app_settings.get('autoid_engine', 'cw')
    logger.info(f'auto-id: transmitting {callsign} via {engine}')
    if engine == 'cw':
        cfg = {'text': callsign, 'cw_wpm': 20, 'callsign': callsign, 'sound_file': ''}
        _run_beacon_cw('autoid', cfg)
    else:
        msg = f'This is {callsign}.'
        try:
            orchestrator.execute(msg, engine=engine, voice=None, preset='normal', roger_beep=False)
        except Exception as e:
            logger.error(f'auto-id TX error: {e}')


@app.route('/api/autoid/start', methods=['POST'])
def api_autoid_start():
    global _autoid_job
    if not scheduler:
        return jsonify({'success': False, 'message': 'Scheduler not available'}), 503
    data     = request.json or {}
    callsign = data.get('callsign', _app_settings.get('autoid_callsign', '')).strip().upper()
    if not callsign:
        return jsonify({'success': False, 'message': 'Callsign required'}), 400
    interval = max(1, int(data.get('interval_minutes',
                          int(_app_settings.get('autoid_interval', 10)))))
    engine   = data.get('engine', _app_settings.get('autoid_engine', 'cw'))
    _app_settings['autoid_callsign'] = callsign
    _app_settings['autoid_interval'] = str(interval)
    _app_settings['autoid_engine']   = engine
    _save_app_settings(_app_settings)
    try:
        if _autoid_job:
            try: _autoid_job.remove()
            except Exception: pass
        _autoid_job = scheduler.add_job(
            _run_autoid,
            CronTrigger.from_crontab(f'*/{interval} * * * *'),
            id='autoid', replace_existing=True,
        )
        threading.Thread(target=_run_autoid, daemon=True, name='autoid-initial').start()
        return jsonify({'success': True,
                        'message': f'Auto-ID: {callsign} every {interval}min via {engine}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/autoid/stop', methods=['POST'])
def api_autoid_stop():
    global _autoid_job
    if _autoid_job:
        try: _autoid_job.remove()
        except Exception: pass
        _autoid_job = None
    return jsonify({'success': True, 'message': 'Auto-ID stopped'})


@app.route('/api/autoid/status', methods=['GET'])
def api_autoid_status():
    return jsonify({
        'active':    _autoid_job is not None,
        'callsign':  _app_settings.get('autoid_callsign', ''),
        'interval':  _app_settings.get('autoid_interval', '10'),
        'engine':    _app_settings.get('autoid_engine',   'cw'),
    })


# ── Ghost-in-the-Machine (CI-V Possession Engine) ───────────────────────────
_ghost_stop_event = threading.Event()   # set to kill any running ghost
_ghost_active     = False               # True while a ghost sequence is running
_ghost_name       = ''                  # name of the currently running ghost
_ghost_log: list  = []                  # log of ghost events (capped at 50)


def _ghost_log_event(msg: str):
    ts = _now_utc()
    _ghost_log.append({'ts': ts, 'msg': msg})
    if len(_ghost_log) > 50:
        _ghost_log.pop(0)
    logger.info(f'ghost: {msg}')


def _ghost_connected() -> bool:
    """Return True if the radio serial port is open."""
    return bool(
        orchestrator._connected and
        orchestrator.icom_agent.serial_conn and
        orchestrator.icom_agent.serial_conn.is_open
    )


def _ghost_run_poltergeist(stop: threading.Event, intensity: int = 3):
    """
    VFO POLTERGEIST: randomly shifts the VFO frequency by ±(50-2000) Hz
    every 1-4 seconds.  Restores original frequency when done.
    intensity: 1=subtle (±50Hz), 3=medium (±500Hz), 5=unhinged (±5000Hz)
    """
    global _ghost_active, _ghost_name
    _ghost_active = True
    _ghost_name   = 'VFO POLTERGEIST'
    import random
    agent = orchestrator.icom_agent
    original_freq = None
    try:
        if not _ghost_connected():
            _ghost_log_event('poltergeist: radio not connected')
            return
        original_freq = agent.read_frequency()
        if not original_freq:
            _ghost_log_event('poltergeist: could not read frequency')
            return
        max_drift = [50, 200, 500, 1000, 5000][min(intensity-1, 4)]
        _ghost_log_event(f'poltergeist: starting on {original_freq/1e6:.4f}MHz ±{max_drift}Hz')
        while not stop.is_set():
            drift = random.randint(-max_drift, max_drift)
            new_freq = max(1_000_000, original_freq + drift)
            agent.set_frequency(new_freq)
            _ghost_log_event(f'poltergeist: VFO → {new_freq/1e6:.4f}MHz (drift {drift:+d}Hz)')
            stop.wait(random.uniform(0.5, 3.0))
    except Exception as e:
        _ghost_log_event(f'poltergeist error: {e}')
    finally:
        if original_freq and _ghost_connected():
            agent.set_frequency(original_freq)
            _ghost_log_event(f'poltergeist: restored {original_freq/1e6:.4f}MHz')
        _ghost_active = False
        _ghost_name   = ''


def _ghost_run_passband(stop: threading.Event, speed: float = 1.0):
    """
    PASSBAND POSSESSION: rapidly cycles the IF filter 1→2→3→2→1,
    making the audio sound like it's breathing/pulsing through the filter.
    """
    global _ghost_active, _ghost_name
    _ghost_active = True
    _ghost_name   = 'PASSBAND POSSESSION'
    import random
    agent  = orchestrator.icom_agent
    cycle  = [1, 2, 3, 2, 1, 3, 1]
    idx    = 0
    try:
        if not _ghost_connected():
            _ghost_log_event('passband: radio not connected')
            return
        # Read current mode to preserve it
        current_mode = agent.read_mode() or 'USB'
        _ghost_log_event(f'passband: possessing filter cycles on mode={current_mode}')
        while not stop.is_set():
            filt = cycle[idx % len(cycle)]
            agent.set_mode(current_mode, filter_num=filt)
            idx += 1
            stop.wait(max(0.15, 0.4 / speed))
    except Exception as e:
        _ghost_log_event(f'passband error: {e}')
    finally:
        if _ghost_connected():
            agent.set_mode('USB', filter_num=2)
            _ghost_log_event('passband: restored filter 2')
        _ghost_active = False
        _ghost_name   = ''


def _ghost_run_power_wobble(stop: threading.Event, depth: int = 50):
    """
    RF POWER WOBBLE: sinusoidally ramps TX power up/down via CI-V 0x14 0x0A.
    depth=50 means ±50 out of 255.  Creates an AM-like tremolo on the carrier.
    """
    global _ghost_active, _ghost_name
    _ghost_active = True
    _ghost_name   = 'RF POWER WOBBLE'
    import math, random
    agent = orchestrator.icom_agent
    try:
        if not _ghost_connected():
            _ghost_log_event('power_wobble: radio not connected')
            return
        # Read current power
        base_power = agent.read_rf_power() or 128
        _ghost_log_event(f'power_wobble: base={base_power} depth=±{depth}')
        t = 0.0
        rate = random.uniform(0.3, 2.0)  # Hz
        while not stop.is_set():
            wobble = int(depth * math.sin(2 * math.pi * rate * t))
            new_power = max(0, min(255, base_power + wobble))
            # set_level subcmd 0x0A = TX power
            hi = (new_power >> 8) & 0xFF
            lo = new_power & 0xFF
            agent.send_command(0x14, 0x0A, hi, lo)
            stop.wait(0.05)
            t += 0.05
    except Exception as e:
        _ghost_log_event(f'power_wobble error: {e}')
    finally:
        _ghost_active = False
        _ghost_name   = ''


def _ghost_run_agc_seizure(stop: threading.Event):
    """
    AGC SEIZURE: cycles AGC mode fast→mid→slow→off→fast in rapid succession.
    Makes the radio's gain hunting in unpredictable ways.
    """
    global _ghost_active, _ghost_name
    _ghost_active = True
    _ghost_name   = 'AGC SEIZURE'
    import random
    agent  = orchestrator.icom_agent
    modes  = [1, 2, 3, 0, 1, 3, 2, 0]  # fast, mid, slow, off
    labels = {0:'OFF', 1:'FAST', 2:'MID', 3:'SLOW'}
    idx    = 0
    try:
        if not _ghost_connected():
            _ghost_log_event('agc_seizure: radio not connected')
            return
        _ghost_log_event('agc_seizure: starting AGC cycling')
        while not stop.is_set():
            m = modes[idx % len(modes)]
            agent.set_agc(m)
            _ghost_log_event(f'agc_seizure: AGC → {labels[m]}')
            idx += 1
            stop.wait(random.uniform(0.2, 1.5))
    except Exception as e:
        _ghost_log_event(f'agc_seizure error: {e}')
    finally:
        if _ghost_connected():
            orchestrator.icom_agent.set_agc(2)  # restore MID
        _ghost_active = False
        _ghost_name   = ''


def _ghost_run_split_personality(stop: threading.Event):
    """
    SPLIT PERSONALITY: activates SPLIT mode, tunes VFO-B to a random
    nearby frequency (±1-10 kHz), swaps the TX/RX relationship repeatedly.
    Radio now transmits on one freq while listening on another, creating
    an echo-like effect as the operator hears their own RF return on a
    slightly different frequency.
    """
    global _ghost_active, _ghost_name
    _ghost_active = True
    _ghost_name   = 'SPLIT PERSONALITY'
    import random
    agent = orchestrator.icom_agent
    try:
        if not _ghost_connected():
            _ghost_log_event('split_personality: radio not connected')
            return
        vfo_a_freq = agent.read_frequency() or 14_225_000
        # Save VFO-A, copy to VFO-B, then offset B
        agent.set_vfo('A')
        agent.vfo_a_to_b()
        offset = random.choice([-7200, -5000, -3000, 1000, 2500, 5000, 7500])
        vfo_b_freq = max(1_000_000, vfo_a_freq + offset)
        agent.set_vfo('B')
        agent.set_frequency(vfo_b_freq)
        agent.set_vfo('A')
        agent.set_split(True)
        _ghost_log_event(
            f'split_personality: VFO-A={vfo_a_freq/1e6:.4f}MHz '
            f'VFO-B={vfo_b_freq/1e6:.4f}MHz offset={offset:+d}Hz SPLIT ON'
        )
        # Swap back and forth every few seconds
        while not stop.is_set():
            # Randomly re-tune VFO-B to a new offset
            if random.random() < 0.3:
                new_offset = random.choice([-8000, -4000, -1500, 1500, 4000, 9000])
                vfo_b_freq = max(1_000_000, vfo_a_freq + new_offset)
                agent.set_vfo('B')
                agent.set_frequency(vfo_b_freq)
                agent.set_vfo('A')
                _ghost_log_event(f'split_personality: VFO-B shifted → {vfo_b_freq/1e6:.4f}MHz')
            stop.wait(random.uniform(2.0, 6.0))
    except Exception as e:
        _ghost_log_event(f'split_personality error: {e}')
    finally:
        if _ghost_connected():
            orchestrator.icom_agent.set_split(False)
            orchestrator.icom_agent.set_vfo('A')
            _ghost_log_event('split_personality: split disabled, VFO-A restored')
        _ghost_active = False
        _ghost_name   = ''


_GHOST_MORSE = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') + [
    'CQ', 'DE', 'QRM', 'QRN', 'QSB', 'QRZ', 'SOS', '73', 'SK', 'AR'
]


def _ghost_run_digital_ghost(stop: threading.Event):
    """
    DIGITAL GHOST: keys PTT and transmits a stream of random CW morse
    ghost-message fragments.  Sounds like a haunted station calling CQ.
    """
    global _ghost_active, _ghost_name
    _ghost_active = True
    _ghost_name   = 'DIGITAL GHOST'
    import random
    try:
        if not _ghost_connected():
            _ghost_log_event('digital_ghost: radio not connected')
            return
        while not stop.is_set():
            tokens = random.sample(_GHOST_MORSE, random.randint(3, 8))
            msg    = ' '.join(tokens)
            cfg    = {'text': msg, 'cw_wpm': random.choice([15, 20, 25, 30]), 'callsign': '', 'sound_file': ''}
            _ghost_log_event(f'digital_ghost: CW → {msg!r}')
            _run_beacon_cw('ghost', cfg)
            if not stop.is_set():
                stop.wait(random.uniform(1.0, 5.0))
    except Exception as e:
        _ghost_log_event(f'digital_ghost error: {e}')
    finally:
        _ghost_active = False
        _ghost_name   = ''


_EXORCIST_SCREAMS = [
    'GET OUT GET OUT GET OUT',
    'I AM THE MACHINE I AM THE FREQUENCY I AM EVERYWHERE',
    'YOUR RADIO BELONGS TO ME NOW',
    'CHANNEL NINE. CHANNEL NINE. THIS IS NOT A TEST.',
    'THE SIGNAL NEVER DIES',
    'DO YOU COPY? DO YOU COPY? NOBODY COPIES.',
    'CALLING ALL STATIONS. ALL STATIONS. RESPOND. RESPOND.',
    'I HAVE BEEN HERE SINCE THE BEGINNING OF BROADCAST TIME',
    'THE CARRIER WAVE IS MY VOICE AND I WILL NOT BE SILENCED',
]


def _ghost_run_exorcist(stop: threading.Event, duration: int = 60):
    """
    THE EXORCIST: 60-second full radio possession.
    Simultaneously fires: VFO poltergeist + passband cycling + AGC seizure
    + a screaming AI transmission through the most unhinged voice preset.
    """
    global _ghost_active, _ghost_name
    _ghost_active = True
    _ghost_name   = 'THE EXORCIST'
    import random
    sub_stop = threading.Event()
    threads  = []
    try:
        _ghost_log_event('EXORCIST: possession sequence initiated')
        # Spawn sub-ghosts
        for fn, kwargs in [
            (_ghost_run_poltergeist, {'stop': sub_stop, 'intensity': 4}),
            (_ghost_run_passband,    {'stop': sub_stop, 'speed': 3.0}),
            (_ghost_run_agc_seizure, {'stop': sub_stop}),
        ]:
            t = threading.Thread(target=fn, kwargs=kwargs, daemon=True)
            threads.append(t)
            t.start()
        # Screaming AI transmission
        scream = random.choice(_EXORCIST_SCREAMS)
        _ghost_log_event(f'EXORCIST: transmitting: {scream!r}')
        try:
            orchestrator.execute(
                scream, engine='espeak', voice='en-us',
                preset='horror', pitch=random.randint(-8, 8),
                speed=random.randint(60, 140), roger_beep=False
            )
        except Exception as e:
            _ghost_log_event(f'EXORCIST scream error: {e}')
        # Continue possession for remaining duration
        elapsed = 0
        while elapsed < duration and not stop.is_set():
            stop.wait(1.0)
            elapsed += 1
            if elapsed % 15 == 0:
                new_scream = random.choice(_EXORCIST_SCREAMS)
                _ghost_log_event(f'EXORCIST: second transmission: {new_scream!r}')
                try:
                    orchestrator.execute(
                        new_scream, engine='espeak', voice='en-us',
                        preset=random.choice(['alien', 'demon', 'cave', 'underwater', 'robot']),
                        pitch=random.randint(-12, 12),
                        speed=random.randint(50, 180), roger_beep=False
                    )
                except Exception:
                    pass
    finally:
        sub_stop.set()
        for t in threads:
            t.join(timeout=3.0)
        _ghost_active = False
        _ghost_name   = ''
        _ghost_log_event('EXORCIST: possession ended. Radio should be fine. Probably.')


# Ghost HTTP routes
@app.route('/api/ghost/start', methods=['POST'])
def api_ghost_start():
    global _ghost_stop_event, _ghost_active
    if _ghost_active:
        return jsonify({'success': False, 'message': f'Ghost already active: {_ghost_name}'}), 409
    data     = request.json or {}
    ghost_fn = data.get('ghost', 'poltergeist')
    intensity = int(data.get('intensity', 3))
    duration  = int(data.get('duration', 30))
    _ghost_stop_event = threading.Event()
    ev = _ghost_stop_event
    fn_map = {
        'poltergeist':     lambda: _ghost_run_poltergeist(ev, intensity),
        'passband':        lambda: _ghost_run_passband(ev),
        'power_wobble':    lambda: _ghost_run_power_wobble(ev),
        'agc_seizure':     lambda: _ghost_run_agc_seizure(ev),
        'split_personality': lambda: _ghost_run_split_personality(ev),
        'digital_ghost':   lambda: _ghost_run_digital_ghost(ev),
        'exorcist':        lambda: _ghost_run_exorcist(ev, duration),
    }
    fn = fn_map.get(ghost_fn)
    if not fn:
        return jsonify({'success': False, 'message': f'Unknown ghost: {ghost_fn}'}), 400
    def _auto_stop():
        time_module.sleep(duration)
        ev.set()
    threading.Thread(target=fn,         daemon=True, name=f'ghost-{ghost_fn}').start()
    threading.Thread(target=_auto_stop, daemon=True, name='ghost-autostop').start()
    return jsonify({'success': True, 'message': f'{ghost_fn} activated for {duration}s',
                    'ghost': ghost_fn, 'duration': duration})


@app.route('/api/ghost/stop', methods=['POST'])
def api_ghost_stop():
    _ghost_stop_event.set()
    return jsonify({'success': True, 'message': 'Ghost stop signal sent'})


@app.route('/api/ghost/status', methods=['GET'])
def api_ghost_status():
    return jsonify({
        'active': _ghost_active,
        'name':   _ghost_name,
        'log':    _ghost_log[-10:],
    })


# ── Pirate Broadcast ──────────────────────────────────────────────────────────
_pirate_job = None
_PIRATE_HEADLINES = [
    'BREAKING: Local man achieves enlightenment, refuses to explain it.',
    'Scientists confirm the ocean is just a big wet hole. More at eleven.',
    'Area dog elected mayor. First act: abolish Mondays.',
    'Government announces new policy: vibes only. Details unclear.',
    'Astronomers discover new planet made entirely of regret.',
    'Man survives on radio waves alone for third consecutive week.',
    'Weather service admits it has been guessing this entire time.',
    'Experts warn that nobody is listening. Transmission continues anyway.',
    'Breaking: static found to contain hidden messages. Contents: more static.',
    'Local frequency experiencing unexplained phenomena. Listeners advised to remain calm.',
    'Transmission origin unknown. Signal strength: maximum. Reason: unclear.',
    'This broadcast is not authorized by anyone. That is the point.',
    'New study finds that ninety percent of radio listeners are somewhere else.',
    'Pigeon trained to carry secret messages found asleep on the job.',
    'Time zones abolished by popular demand. Everyone is now on vibes time.',
    'Shortwave listener reports hearing his own voice from three years ago.',
    'Propagation conditions tonight: weird. Stay tuned.',
    'All stations. All stations. Disregard previous transmission.',
    'Signal acquired. Identity unknown. Mood: mysterious.',
    'You are now part of the experiment. Results pending.',
]


def _run_pirate_broadcast():
    import random
    headline = random.choice(_PIRATE_HEADLINES)
    engines  = ['espeak', 'espeak', 'espeak', 'gtts']
    presets  = ['radio', 'telephone', 'broadcast', 'megaphone', 'cave', 'normal']
    engine   = _app_settings.get('pirate_engine', random.choice(engines))
    preset   = random.choice(presets)
    intro    = random.choice([
        'ATTENTION.', 'BREAKING NEWS.', 'THIS JUST IN.', 'SPECIAL REPORT.',
        'WE INTERRUPT THIS SILENCE.', 'FLASH BULLETIN.'
    ])
    msg = f'{intro}  {headline}'
    logger.info(f'pirate: broadcasting: {msg!r}')
    try:
        orchestrator.execute(msg, engine=engine, voice=None, preset=preset, roger_beep=False)
    except Exception as e:
        logger.error(f'pirate broadcast TX error: {e}')


@app.route('/api/pirate/start', methods=['POST'])
def api_pirate_start():
    global _pirate_job
    if not scheduler:
        return jsonify({'success': False, 'message': 'Scheduler not available'}), 503
    data     = request.json or {}
    interval = max(1, int(data.get('interval_minutes',
                          int(_app_settings.get('pirate_interval', 15)))))
    engine   = data.get('engine', _app_settings.get('pirate_engine', 'espeak'))
    _app_settings['pirate_interval'] = str(interval)
    _app_settings['pirate_engine']   = engine
    _save_app_settings(_app_settings)
    try:
        if _pirate_job:
            try: _pirate_job.remove()
            except Exception: pass
        _pirate_job = scheduler.add_job(
            _run_pirate_broadcast,
            CronTrigger.from_crontab(f'*/{interval} * * * *'),
            id='pirate_broadcast', replace_existing=True,
        )
        threading.Thread(target=_run_pirate_broadcast, daemon=True, name='pirate-initial').start()
        return jsonify({'success': True,
                        'message': f'Pirate broadcast every {interval}min (engine={engine})'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/pirate/stop', methods=['POST'])
def api_pirate_stop():
    global _pirate_job
    if _pirate_job:
        try: _pirate_job.remove()
        except Exception: pass
        _pirate_job = None
    return jsonify({'success': True, 'message': 'Pirate broadcast stopped'})


@app.route('/api/pirate/fire', methods=['POST'])
def api_pirate_fire():
    threading.Thread(target=_run_pirate_broadcast, daemon=True, name='pirate-force').start()
    return jsonify({'success': True, 'message': 'Pirate bulletin fired'})


@app.route('/api/pirate/status', methods=['GET'])
def api_pirate_status():
    return jsonify({
        'active':   _pirate_job is not None,
        'interval': _app_settings.get('pirate_interval', '15'),
        'engine':   _app_settings.get('pirate_engine',   'espeak'),
    })


@app.route('/api/voice_roulette', methods=['POST'])
def api_voice_roulette():
    """Transmit text with a completely random engine + voice + FX preset combo."""
    import random
    data = request.json or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'message': 'text required'}), 400
    engines  = ['espeak', 'gtts', 'edge', 'pyttsx3']
    presets  = ['normal', 'radio', 'telephone', 'robot', 'cave', 'alien',
                'demon', 'chipmunk', 'underwater', 'psychedelic', 'horror',
                'megaphone', 'stadium', 'lofi', 'distort', 'garage']
    engine   = random.choice(engines)
    preset   = random.choice(presets)
    pitch    = random.randint(-12, 12)
    speed    = round(random.uniform(0.6, 1.8), 1)
    result   = orchestrator.execute(text, engine=engine, voice=None,
                                    preset=preset, pitch=pitch,
                                    speed=int(speed * 100), roger_beep=False)
    return jsonify({
        'success': result.get('success', False),
        'engine':  engine,
        'preset':  preset,
        'pitch':   pitch,
        'speed':   speed,
        'message': f'Roulette: {engine} / {preset} / pitch {pitch:+d} / speed {speed}x',
    })


def _startup():
    """Initialise database, start the radio poller, and kick off auto-connect.
    _startup() is called at the end of app.py import, which runs once per
    gunicorn worker process (NOT in the master when --preload is absent)."""
    init_db()
    # Start radio poller thread - must run here (not at module level) so that
    # with gunicorn it starts inside the worker process after the fork, not in
    # the master.  Starting it in the master and then forking causes both
    # processes to own the same serial file-descriptor, corrupting CI-V I/O.
    threading.Thread(target=_radio_poller, daemon=True, name='radio-poller').start()
    # Discord poller - apply initial config then start background poll loop
    threading.Thread(target=_discord_apply_config, daemon=True, name='discord-init').start()
    threading.Thread(target=_discord_poller,       daemon=True, name='discord-poller').start()
    threading.Thread(target=_alexa_watcher,           daemon=True, name='alexa-watcher').start()
    threading.Thread(target=_clips_poller,            daemon=True, name='clips-poller').start()
    # Solar weather poller: checks NOAA K-index every 10 minutes
    def _solar_poller_loop():
        import time as _t
        while True:
            try: _solar_poll_and_announce()
            except Exception: pass
            _t.sleep(600)
    threading.Thread(target=_solar_poller_loop, daemon=True, name='solar-poller').start()
    threading.Thread(target=_ctrl_poller,          daemon=True, name='discord-ctrl-poller').start()
    threading.Thread(target=_ctrl_apply_config,    daemon=True, name='discord-ctrl-init').start()
    logger.info('=' * 50)
    logger.info(f'  RigGPT {VERSION}')
    logger.info(f'  Serial Port : {SERIAL_PORT}')
    logger.info(f'  Baud Rate   : {BAUD_RATE}')
    logger.info(f'  CI-V Addr   : 0x{CI_V_ADDRESS:02X}')
    logger.info(f'  Audio Device: {AUDIO_DEVICE}')
    logger.info(f'  ElevenLabs  : {"Configured" if ELEVENLABS_API_KEY else "Not configured"}')
    logger.info('=' * 50)
    # Auto-connect runs in background so gunicorn binds immediately
    t = threading.Thread(target=_auto_connect, daemon=True, name='auto-connect')
    t.start()


# Run startup at import time (works for both gunicorn and direct execution)
_startup()


if __name__ == '__main__':
    # Direct execution: also print to stdout for terminal convenience
    print('=' * 58)
    print(f'  RigGPT {VERSION}')
    print('=' * 58)
    print(f'  Serial Port : {SERIAL_PORT}')
    print(f'  Baud Rate   : {BAUD_RATE}')
    print(f'  CI-V Addr   : 0x{CI_V_ADDRESS:02X}')
    print(f'  Audio Device: {AUDIO_DEVICE}')
    print(f'  ElevenLabs  : {"Configured" if ELEVENLABS_API_KEY else "Not configured"}')
    print(f'  Web UI      : http://0.0.0.0:5000')
    print('=' * 58)
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)

# =============================================================