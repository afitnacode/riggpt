#!/bin/bash
# riggpt-cron-setup.sh
# Run this on the Docker host (root@rtx5070ti) to set up the delta ingest cron.
# Prerequisites: Python3, pip3, and network access to Qdrant + Ollama containers.
#
# Usage: sudo bash riggpt-cron-setup.sh
# ─────────────────────────────────────────────────────────────────────────────

set -e

INGEST_DIR="/opt/riggpt-memory"
INGEST_SCRIPT="$INGEST_DIR/riggpt-ingest.py"
LOG_FILE="/var/log/riggpt-ingest.log"
CRON_FILE="/etc/cron.d/riggpt-memory"
CHECKPOINT_FILE="/opt/riggpt-memory/memory_checkpoint.json"
CRON_USER="root"

echo "=============================================="
echo "  RigGPT Memory — Docker Host Cron Setup"
echo "=============================================="

# ── 1. Install Python deps ──────────────────────────────────────────────────
echo "[1/4] Installing Python dependencies..."
pip3 install requests qdrant-client --break-system-packages -q \
    --root-user-action=ignore
echo "  OK: requests, qdrant-client"

# ── 2. Pull embedding model into Ollama container ───────────────────────────
echo "[2/4] Pulling nomic-embed-text into Ollama container..."
docker exec ollama ollama pull nomic-embed-text
echo "  OK: nomic-embed-text pulled"

# ── 3. Create ingest directory and copy script ─────────────────────────────
echo "[3/4] Setting up $INGEST_DIR..."
mkdir -p "$INGEST_DIR"

# Copy riggpt-ingest.py from wherever you extracted the zip.
# If you haven't yet, copy it manually:
#   cp /path/to/RigGPT-v2.12.17/v2_12_8_pkg/memory/riggpt-ingest.py $INGEST_DIR/
if [ ! -f "$INGEST_SCRIPT" ]; then
    echo ""
    echo "  !! riggpt-ingest.py not found at $INGEST_SCRIPT"
    echo "  !! Copy it there, then re-run this script, or create the cron manually."
    echo "  !! Expected path: $INGEST_SCRIPT"
    echo ""
fi

# Write the credentials wrapper script (keeps secrets out of cron env)
cat > "$INGEST_DIR/run-delta.sh" << 'WRAPPER'
#!/bin/bash
# Delta ingest wrapper — edit DISCORD_TOKEN and DISCORD_CHANNEL_ID below.
# This file is only readable by root (chmod 700).

export DISCORD_TOKEN="REPLACE_WITH_YOUR_BOT_TOKEN"
export DISCORD_CHANNEL_ID="REPLACE_WITH_YOUR_CHANNEL_ID"

# Qdrant and Ollama are on this host — no need to set those env vars.
# They default to 192.168.40.15:6333 and 192.168.40.15:11434.

exec python3 /opt/riggpt-memory/riggpt-ingest.py --delta
WRAPPER

chmod 700 "$INGEST_DIR/run-delta.sh"
echo "  Created: $INGEST_DIR/run-delta.sh"
echo ""
echo "  !! EDIT THIS FILE NOW before the cron runs:"
echo "  !!   nano $INGEST_DIR/run-delta.sh"
echo "  !! Set DISCORD_TOKEN and DISCORD_CHANNEL_ID."
echo ""

# ── 4. Install cron job ─────────────────────────────────────────────────────
echo "[4/4] Installing cron job at $CRON_FILE..."

cat > "$CRON_FILE" << CRONEOF
# RigGPT Memory — incremental Discord channel ingest
# Runs every 4 hours. Logs to $LOG_FILE.
# To disable: rm $CRON_FILE  or  comment out the line below.
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

0 */4 * * * $CRON_USER $INGEST_DIR/run-delta.sh >> $LOG_FILE 2>&1
CRONEOF

chmod 644 "$CRON_FILE"
echo "  Installed: $CRON_FILE"

# Ensure log file exists and is writable
touch "$LOG_FILE"
chmod 644 "$LOG_FILE"

echo ""
echo "=============================================="
echo "  Setup complete."
echo ""
echo "  NEXT STEPS:"
echo ""
echo "  1. Edit credentials:"
echo "     nano $INGEST_DIR/run-delta.sh"
echo ""
echo "  2. Run the one-time FULL ingest (do this first, on any machine"
echo "     that has the Discord token set):"
echo "     DISCORD_TOKEN=... DISCORD_CHANNEL_ID=... \\"
echo "     python3 $INGEST_SCRIPT --full"
echo ""
echo "  3. After full ingest, test the delta manually:"
echo "     $INGEST_DIR/run-delta.sh"
echo "     tail -f $LOG_FILE"
echo ""
echo "  4. Check Qdrant collections:"
echo "     python3 $INGEST_SCRIPT --status"
echo ""
echo "  Cron schedule: every 4 hours"
echo "  Log file:      $LOG_FILE"
echo "  Checkpoint:    $CHECKPOINT_FILE"
echo "=============================================="
