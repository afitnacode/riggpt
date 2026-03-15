#!/bin/bash
# RigGPT v2.11.15 -- Hot-patch: copy files and restart
# Run from the unzipped package directory: sudo bash patch_server.sh
set -e

INSTALL_DIR="/opt/riggpt"
SERVICE="riggpt"
SVC_USER="riggpt"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION="2.11.15"

echo "=== RigGPT v${VERSION} Patch ==="

if [ ! -d "$INSTALL_DIR" ]; then
    echo "ERROR: $INSTALL_DIR not found. Run INSTALL.sh first."
    exit 1
fi

# Timestamped backups
TS=$(date +%Y%m%d_%H%M%S)
cp "$INSTALL_DIR/app.py"               "$INSTALL_DIR/app.py.bak.${TS}"
cp "$INSTALL_DIR/templates/index.html" "$INSTALL_DIR/templates/index.html.bak.${TS}"
echo "  Backups created (.bak.${TS})"

# Copy new files
cp "$SCRIPT_DIR/app.py"               "$INSTALL_DIR/app.py"
cp "$SCRIPT_DIR/templates/index.html" "$INSTALL_DIR/templates/index.html"
[ -f "$SCRIPT_DIR/waterfall_image.py" ] && cp "$SCRIPT_DIR/waterfall_image.py" "$INSTALL_DIR/waterfall_image.py"
[ -f "$SCRIPT_DIR/api_keys.py" ]        && cp "$SCRIPT_DIR/api_keys.py"        "$INSTALL_DIR/api_keys.py"
chown -R "$SVC_USER:dialout" "$INSTALL_DIR" 2>/dev/null || true
echo "  Files copied."

UNIT_FILE="/etc/systemd/system/${SERVICE}.service"
UNIT_CHANGED=0

# Remove --preload if present (serial port fork safety)
if [ -f "$UNIT_FILE" ] && grep -q "preload" "$UNIT_FILE"; then
    echo "  Removing --preload from gunicorn flags..."
    sed -i 's| --preload||g; s| --capture-output||g' "$UNIT_FILE"
    UNIT_CHANGED=1
fi

# Ensure PULSE_SERVER bypass is set
if [ -f "$UNIT_FILE" ] && ! grep -q "PULSE_SERVER" "$UNIT_FILE"; then
    echo "  Patching unit: adding PULSE_SERVER + HOME env vars..."
    SVC_HOME="/home/riggpt"
    sed -i "/^ExecStart=/i Environment=\"HOME=${SVC_HOME}\"\nEnvironment=\"PULSE_SERVER=\"\nEnvironment=\"ALSA_CONFIG_PATH=/usr/share/alsa/alsa.conf\"" "$UNIT_FILE"
    UNIT_CHANGED=1
fi

if [ "$UNIT_CHANGED" = "1" ]; then
    systemctl daemon-reload
    echo "  Unit reloaded."
fi

# Clean root-owned runtime artifacts
for f in "$INSTALL_DIR/gunicorn.ctl" "$INSTALL_DIR/gunicorn.pid"; do
    [ -f "$f" ] && rm -f "$f" && echo "  Cleaned: $f"
done
chown -R "$SVC_USER:dialout" "$INSTALL_DIR" 2>/dev/null || true

systemctl restart "$SERVICE"
echo -n "  Waiting for service on port 5000"
BOUND=0
for i in $(seq 1 60); do
    sleep 1; echo -n "."
    CODE=$(curl -s -o /dev/null -w "%{http_code}" --max-time 2 \
           "http://localhost:5000/api/status" 2>/dev/null || echo "0")
    [ "$CODE" = "200" ] && BOUND=1 && break
done
echo ""

if [ "$BOUND" = "1" ]; then
    echo "  Service responding OK."
else
    echo "  WARNING: service did not respond within 60s"
    echo "  Check logs: journalctl -u $SERVICE -n 50"
fi

echo ""
echo "  Status: $(systemctl is-active $SERVICE)"
echo ""
echo "  Route check:"
for ep in /api/status /api/system/health /api/ai/config; do
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" --max-time 5 \
           "http://localhost:5000${ep}" 2>/dev/null || echo "ERR")
    echo "    GET $ep -> HTTP $HTTP  $([ "$HTTP" = "200" ] && echo OK || echo FAIL)"
done
echo "Done."
