#!/usr/bin/env bash
#
# Install the daily 09:00 ads tick as a launchd LaunchAgent.
# Reversible: launchctl bootout gui/$UID com.williamj.ads-tick (or run with
# UNINSTALL=1).
#
set -euo pipefail

PLIST_SRC="$(CDPATH= cd -- "$(dirname "$0")" && pwd)/tick.launchd.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.williamj.ads-tick.plist"
LABEL="com.williamj.ads-tick"

if [ "${UNINSTALL:-0}" = "1" ]; then
  launchctl bootout "gui/$(id -u)" "$LABEL" 2>/dev/null || true
  rm -f "$PLIST_DST"
  echo "removed $PLIST_DST"
  exit 0
fi

mkdir -p "$HOME/Library/LaunchAgents"
cp "$PLIST_SRC" "$PLIST_DST"
launchctl bootout "gui/$(id -u)" "$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST_DST"
echo "installed $PLIST_DST (daily 09:00 tick)"
