#!/usr/bin/env bash
# Owner-run verification only. Builds temporary fixtures; never publishes.
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ -x .venv/bin/python ]]; then
  site_python=.venv/bin/python
else
  site_python=python3
fi
# Check imports with the exact interpreter used by every Python gate below.
if ! "$site_python" -c 'import yaml; import sys; __import__("tomllib" if sys.version_info >= (3, 11) else "tomli")' >/dev/null 2>&1; then
  printf 'Python dependencies are unavailable in %s. No tests were run.\n' "$site_python" >&2
  printf 'From the repository root, run:\n\n' >&2
  if [[ ! -x .venv/bin/python ]]; then
    printf '  python3 -m venv .venv\n' >&2
  fi
  printf '  .venv/bin/python -m pip install -r requirements.txt\n  bash scripts/verify-local.sh\n\n' >&2
  exit 1
fi
"$site_python" -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.cjs
"$site_python" scripts/feature_docs.py --check
"$site_python" scripts/release_check.py --staging --base-url https://fixture-review.org/subpath/ --report /tmp/jeff-does-doors-preview-report.json
if [[ -d .git || -f .git ]]; then git diff --check; fi
printf '\nLocal checks completed. No deployment performed. Report: /tmp/jeff-does-doors-preview-report.json\n'
