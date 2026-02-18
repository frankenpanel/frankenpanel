#!/usr/bin/env bash
# Quick diagnostic for HTTP 502 on FrankenPanel dashboard (port 8090).
# Run on the server: sudo bash scripts/diagnose-502.sh

set -e
PANEL_PORT="${FRANKENPANEL_PORT:-8090}"

echo "=== FrankenPanel 502 diagnostic (port $PANEL_PORT) ==="
echo ""

echo "1. Backend service (frankenpanel-backend):"
systemctl is-active frankenpanel-backend 2>/dev/null || echo "  (not found or not active)"
echo ""

echo "2. Caddy service:"
systemctl is-active caddy 2>/dev/null || echo "  (not found or not active)"
echo ""

echo "3. Listening on port $PANEL_PORT (Caddy):"
ss -tlnp 2>/dev/null | grep -E ":$PANEL_PORT\s" || echo "  (nothing listening)"
echo ""

echo "4. Listening on 127.0.0.1:8000 (backend):"
ss -tlnp 2>/dev/null | grep -E "127.0.0.1:8000|:8000\s" || echo "  (backend not listening - this causes 502)"
echo ""

echo "5. Last 20 lines of backend log:"
journalctl -u frankenpanel-backend -n 20 --no-pager 2>/dev/null || echo "  (cannot read journal)"
echo ""

echo "=== Suggested fix ==="
echo "  sudo systemctl restart frankenpanel-backend"
echo "  sudo systemctl restart caddy"
echo "  Then open http://YOUR_SERVER_IP:$PANEL_PORT"
