#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="cat-notifier"
SERVICE_FILE="$SCRIPT_DIR/$SERVICE_NAME.service"
SYSTEMD_USER_DIR="$HOME/.config/systemd/user"

echo "==> Creating virtual environment..."
python3 -m venv "$SCRIPT_DIR/.venv"
echo "==> Installing dependencies..."
"$SCRIPT_DIR/.venv/bin/pip" install requests

echo "==> Creating systemd user service directory..."
mkdir -p "$SYSTEMD_USER_DIR"

echo "==> Copying service file..."
cp "$SERVICE_FILE" "$SYSTEMD_USER_DIR/$SERVICE_NAME.service"

echo "==> Enabling and starting service..."
systemctl --user daemon-reload
systemctl --user enable "$SERVICE_NAME"
systemctl --user start "$SERVICE_NAME"

echo ""
echo "Done! Service status:"
systemctl --user status "$SERVICE_NAME" --no-pager

echo ""
echo "Useful commands:"
echo "  systemctl --user status $SERVICE_NAME"
echo "  systemctl --user stop $SERVICE_NAME"
echo "  systemctl --user restart $SERVICE_NAME"
echo "  journalctl --user -u $SERVICE_NAME -f"
echo "  tail -f $SCRIPT_DIR/notifier.log"
echo ""
echo "Remember to add the GitHub remote and push:"
echo "  git remote add origin <your-repo-url>"
echo "  git push -u origin master"
