# CLAUDE.md — RigGPT Project Guide

## What this project is
RigGPT is a Flask-based AI ham radio transmission platform for the Icom IC-7610 (and other CI-V compatible radios). It generates TTS speech, keys PTT via CI-V serial, and transmits over the air. Single-file Flask app with a large single-page frontend.

## Repository layout
```
app.py                  Flask backend (~360KB) — all routes, CI-V, TTS, scheduling
templates/index.html    Single-page frontend (~530KB, ~11000 lines) — all UI, JS
INSTALL.sh              Debian installer / upgrade script
gunicorn_conf.py        Gunicorn config — filters noisy access logs
requirements.txt        Python dependencies
README.md               Full feature documentation
api_keys.py             API key manager (not committed — lives on server)
memory/                 Discord ingestion + Qdrant RAG pipeline
waterfall_image.py      Waterfall art encoder
CLAUDE.md               This file — read on startup
```

## Server details
- **Host:** root@radio (192.168.40.10)
- **Service:** `riggpt` (systemd, port 5000)
- **Install dir:** `/opt/riggpt`
- **Python:** 3.13, Debian 13
- **Config files (never touched by installer):**
  - `/home/riggpt/app_settings.json` — all settings
  - `/home/riggpt/api_keys.json` — API credentials

## Current version: v2.12.52

## Version sync rule — ALWAYS update all 5 on every version bump
1. `app.py` docstring header (`RigGPT vX.X.X`)
2. `app.py` `VERSION = 'vX.X.X'` constant
3. `requirements.txt` comment line 1
4. `INSTALL.sh` comment line 1 + `VERSION="X.X.X"` variable
5. `templates/index.html` `<span class="sb-label">vX.X.X</span>` in `#statusbar`

## Deploy workflow
```bash
# From /opt/riggpt (already in the right place):
git pull && bash INSTALL.sh

# Check service after deploy:
systemctl status riggpt
journalctl -u riggpt -n 50
```

## Working style
- Surgical edits only — never rewrite whole files
- Search before reading: `grep -n "pattern" app.py` before opening anything
- For large files use head/tail/grep — do NOT attempt full reads
- `index.html` is ~11000 lines — always grep for the exact anchor before editing
- Preserve existing code style throughout

## Large file warnings
- `index.html` (~530KB, ~11000 lines): grep only, never full read
- `app.py` (~360KB): grep only, never full read
- Both change frequently — always grep for exact text before any edit

## Tab structure (v2.12.52)
```
CONSOLE(1) WF ART(2) SSTV(3) SCHEDULE(4) LOG(5)
CONFIG(6) SYSTEM(7) API CFG(8) AI(9)  ACID TRIP(!)  CLIPS(0)  SPEC OPS(#)
```
- Pane IDs: `pane-dash`, `pane-wfall`, `pane-sstv`,
  `pane-sched`, `pane-hist`, `pane-cfg`, `pane-system`, `pane-apicfg`,
  `pane-ai`, `pane-trip`, `pane-clips`, `pane-specops`
- TABS constant in JS: `['dash','wfall','sstv','sched','hist','cfg','system','apicfg','ai','trip','clips','specops']`
- TX controls are embedded in `pane-dash` (Console tab), not a separate pane
- BEACON was merged into SCHEDULE (50/50 split) in v2.12.52
- `pane-dub` (Trenchtown FX) was removed in v2.12.34; FX/pads live in Clips tab

## Key app.py patterns
- Settings: `POST /api/settings` with allowed-key whitelist → `app_settings.json`
- All new setting keys must be added to the `allowed` set in `api_settings_post()`
- State globals named with leading `_` (e.g. `_ghost_active`, `_pirate_job`)
- Routes follow `@app.route` + `def api_<name>():` naming
- New features need entries in `cfgFlushPresets()` JS AND `_restoreAllSettings()` JS

## Special Ops / Ghost-in-the-Machine
Routes:
- `POST /api/ghost/start {ghost, intensity, duration}` — start a ghost
- `POST /api/ghost/stop` — stop active ghost
- `GET /api/ghost/status` — {active, name, log}
- Ghost names: `poltergeist`, `passband`, `power_wobble`, `agc_seizure`, `split_personality`, `digital_ghost`, `exorcist`

Other Special Ops routes: `numbers_station`, `solar`, `mystery`, `autoid`, `pirate`, `voice_roulette`

## IcomSerialAgent — available CI-V methods
```python
agent.set_frequency(freq_hz)          # cmd 0x05
agent.set_mode(mode_name, filter_num) # cmd 0x06, filter 1/2/3
agent.set_level(sub, value)           # cmd 0x14 (AF=0x01, TX power=0x0A)
agent.set_function(sub, state)        # cmd 0x16
agent.set_split(state)                # cmd 0x0F
agent.set_vfo(vfo)                    # cmd 0x07 (A=0x00, B=0x01)
agent.vfo_swap()                      # cmd 0x07 0xB0
agent.vfo_a_to_b()                    # cmd 0x07 0xA0
agent.set_att(level)                  # cmd 0x11 (0/6/12/18 dB)
agent.set_preamp(level)               # cmd 0x16 0x02
agent.set_agc(mode)                   # cmd 0x16 0x12 (1=fast, 2=mid, 3=slow, 0=off)
agent.set_antenna(ant_num)            # cmd 0x12
agent.read_frequency()
agent.read_mode()
agent.read_rf_power()
agent.read_af_gain()
agent.read_alc()
agent.send_command(*bytes)            # raw CI-V
```

## Config persistence checklist
When adding any new user-facing input field, ALWAYS:
1. Add key to `allowed` set in `api_settings_post()` in `app.py`
2. Add to `cfgFlushPresets()` in `index.html` (the JS that saves on export/change)
3. Add to `_restoreAllSettings(s)` in `index.html` (the JS that restores on page load)

## Things to avoid
- Never read entire index.html or app.py without a grep first
- Never refactor unrelated code during a targeted fix
- Never commit with diverged version strings across the 5 locations
- Never touch `/home/riggpt/app_settings.json` or `api_keys.json` directly
