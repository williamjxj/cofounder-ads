#!/bin/sh
# Recurring generate-and-queue. Example crontab (09:00 local, daily):
#   0 9 * * * /path/to/cofounder-ads/scripts/tick.sh
set -e
ROOT="$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
exec python3 -m engine tick "$@"
