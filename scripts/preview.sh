#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
exec hugo server \
  --config hugo.toml,profiles/jeff-does-doors.toml,hugo-staging.toml \
  --environment staging \
  --cacheDir "${TMPDIR:-/tmp}/jeff-does-doors-hugo-cache" \
  --bind 127.0.0.1 \
  --port 1317 \
  --disableFastRender
