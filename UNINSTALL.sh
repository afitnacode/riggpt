#!/bin/bash
# RigGPT -- Uninstaller
# Removes service, install directory, and service user.
# PRESERVES /home/riggpt/ (persistent config: api keys, settings).
set +e

INSTALL_DIR="/opt/riggpt"
SERVICE="riggpt"
SVC_USER="riggpt"
SVC_HOME="/home/riggpt"

echo "=============================================="
echo "  RigGPT -- Uninstaller"
echo "=============================================="
echo ""
echo "This will remove:"
echo "  - Systemd service: $SERVICE"
echo "  - Install dir:     $INSTALL_DIR"
echo "  - Service user:    $SVC_USER"
echo ""
echo "This will NOT remove:"
echo "  - $SVC_HOME/  (persistent config: api_keys.json, app_settings.json)"
echo "  - The riggpt user account (kept so home dir ownership is valid)"
echo ""
read -r -p "Continue? [y/N] " confirm
[[ "$confirm" =~ ^[Yy]$ ]] || { echo "Cancelled."; exit 0; }

# 1. Stop and disable service
echo ""
echo "[1/5] Stopping service..."
SERVICE_PID=$(systemctl show -p MainPID --value "$SERVICE" 2>/dev/null || true)
if [ -n "$SERVICE_PID" ] && [ "$SERVICE_PID" != "0" ]; then
    systemctl kill --signal=SIGTERM "$SERVICE" 2>/dev/null || true
    sleep 2
    systemctl kill --signal=SIGKILL "$SERVICE" 2>/dev/null || true
fi
for pat in "gunicorn" "app:app" "${INSTALL_DIR}/app.py"; do
    pkill -TERM -f "$pat" 2>/dev/null || true
done
sleep 2
for pat in "gunicorn" "app:app" "${INSTALL_DIR}/app.py"; do
    pkill -KILL -f "$pat" 2>/dev/null || true
done
PORT_PIDS=$(fuser 5000/tcp 2>/dev/null || true)
if [ -n "$PORT_PIDS" ]; then
    echo "  Killing pids on port 5000: $PORT_PIDS"
    kill -KILL $PORT_PIDS 2>/dev/null || true
fi
systemctl stop "$SERVICE" 2>/dev/null && echo "  stopped" || echo "  (already stopped)"
systemctl disable "$SERVICE" 2>/dev/null && echo "  disabled" || echo "  (not enabled)"

# 2. Remove systemd unit
echo "[2/5] Removing systemd unit..."
for f in \
    "/etc/systemd/system/${SERVICE}.service" \
    "/lib/systemd/system/${SERVICE}.service" \
    "/usr/lib/systemd/system/${SERVICE}.service"; do
    [ -f "$f" ] && rm -f "$f" && echo "  removed $f" || true
done
systemctl daemon-reload
systemctl reset-failed 2>/dev/null || true

# 3. Remove install directory
echo "[3/5] Removing install directory..."
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "  removed $INSTALL_DIR"
else
    echo "  (not found)"
fi

# 4. Purge journald logs for this service
echo "[4/5] Purging service logs..."
journalctl --vacuum-files=0 --unit="$SERVICE" 2>/dev/null || true
echo "  done"

# 5. Note: user and home NOT removed
echo "[5/5] Service user retained..."
echo "  User '$SVC_USER' and home '$SVC_HOME' are kept."
echo "  This preserves api_keys.json and app_settings.json across reinstalls."
echo "  To fully remove: userdel -r $SVC_USER"

echo ""
echo "=============================================="
echo "  Uninstall complete."
echo "  Config preserved in: $SVC_HOME/"
echo "  Re-install any time: sudo bash INSTALL.sh"
echo "  Full user removal:   sudo userdel -r $SVC_USER"
echo "=============================================="
