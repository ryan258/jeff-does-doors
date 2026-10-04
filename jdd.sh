#!/usr/bin/env bash
# Short entry point for the existing local-only Hugo preview.
set -euo pipefail

if [[ $# -gt 0 ]]; then
  if [[ $# -eq 1 && ( "$1" == "--help" || "$1" == "-h" ) ]]; then
    printf 'Usage: ./jdd.sh\n\nStart the local Jeff Does Doors preview at http://localhost:1317/.\nOpen http://localhost:1317/survey/ for the door survey.\nPress Ctrl+C to stop. Requires Hugo Extended.\n'
    exit 0
  fi
  printf 'Usage: ./jdd.sh (or ./jdd.sh --help)\n' >&2
  exit 2
fi

jdd_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

if ! command -v hugo >/dev/null 2>&1; then
  printf 'Hugo is not on PATH. Install Hugo Extended, then run ./jdd.sh again.\n' >&2
  exit 1
fi

jdd_hugo_version="$(hugo version)"
if [[ "$jdd_hugo_version" != *+extended* ]]; then
  printf 'Hugo Extended is required to compile the site styles. Found: %s\n' "$jdd_hugo_version" >&2
  exit 1
fi

printf '\nStarting Jeff Does Doors locally…\n\n  Website: http://localhost:1317/\n  Survey:  http://localhost:1317/survey/\n\nKeep this terminal open. Press Ctrl+C to stop.\n\n'
exec bash "$jdd_root/scripts/preview.sh"
