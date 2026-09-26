# Verification and remaining acceptance

## Current status — September 25, 2026

Re-run from a clean checkout after the client-copy cleanup. Every deterministic
gate below was executed, not inherited from the source master's records.

- **19 Python unit tests passed**: source policy, schema validation, feature
  dependency resolution, calendar bound checks, intake acceptance schema,
  transactional artifact swap, release-receipt provenance, and production build
  interlocks.
- **36 Node tests passed**: draft storage expiration, client intake UI states,
  durable D1 receipt idempotency, Cloudflare Email REST `reply_to` delivery
  payload, retry safety, and browser initializers.
- **Release check staging gate passed**: staging artifact audited with no broken
  links, no index leakage, and no OS debris.
- **Feature menu check passed**: `docs/chisel-menu.md` matches the registry.
- **Hugo v0.166.0 build clean**: 14 routes in ~110 ms, 0 deprecation warnings.
- **Generated artifact is 584 KB.** It was 9.5 MB before the unused inherited
  imagery was removed and the hero was re-encoded to WebP.

Run `bash scripts/verify-local.sh` for deterministic local gate execution.

The production gate correctly fails closed at **116 blockers**, of which 109 are
missing owner approvals — `data/evidence.json` is empty by design. The remainder
are real business inputs: production URL, confirmed coverage, inquiry handling,
a verified service area, and a committed Git revision. Real business content
approvals and live Cloudflare deployment remain unperformed.

## Known gaps in this suite

- No test asserts the Functions runtime `INTAKE_SERVICES` list matches
  `data/services.yaml`. These drifted apart once already; the mismatch is
  currently correct but unguarded.
- Deselected modules still carry the source master's excavation-era copy and
  reference imagery that has been deleted. Selecting one fails the release gate
  on a missing source, which is the intended direction of failure, but the copy
  needs a full rewrite before any of them is enabled.
- Browser, device, and assistive-technology checks below are unautomated.

## Manual acceptance still required

- Keyboard and screen-reader traversal on intended browsers, including modal
  focus return and validation errors.
- Real touch devices, zoom, contrast, reduced motion, and longer translated or
  owner-edited labels.
- Email/SMS/call recipient and body checks on actual devices, followed by
  independently confirmed receipt for an authorized test.
- Downloaded-file contents and copy fallback under denied clipboard access.
- No-JavaScript navigation and image fallbacks in an actual browser with
  scripting disabled; current generated-output checks inspect markup only.
- Live hosting, caching, security headers, indexing configuration, external
  listing destination, and post-deployment smoke checks after explicit
  deployment authorization.

## Short reproducible commands

Run from the repository root after the [README setup](../README.md):

```sh
.venv/bin/python -m unittest discover -s tests -p 'test_*.py'
node --test tests/*.test.cjs
.venv/bin/python scripts/feature_docs.py --check
.venv/bin/python scripts/release_check.py --staging \
  --base-url https://fixture-review.org/jeff-does-doors/ \
  --report /tmp/jeff-preview-report.json
```

These are the focused regression set, not a comprehensive browser, device,
accessibility, security, or performance certification. A preview pass means
source structure and generated artifacts met the implemented checks. It does not
establish business facts, customer demand, source rights, delivery, or
publication.
