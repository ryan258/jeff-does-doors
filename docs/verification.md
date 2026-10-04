# Verification and remaining acceptance

## Current revision — October 3, 2026

**Owner-run automated verification passed after two corrections:** deprecated Hugo `site.Data` references were replaced with `hugo.Data`, and the search-ranking fixture was updated to query its barn-door title.

- Ryan’s full run passed all 24 Python tests, including the production-release fixtures.
- That run passed 46 of 47 Node tests; the sole failure was the stale search-ranking fixture. After its correction, Ryan’s targeted rerun passed both tests in `tests/brief-core.test.cjs`. All 47 Node cases therefore have passing evidence across these runs; this is not a claim of a subsequent single full-suite run.
- The follow-up command completed the feature-documentation check, staging source/generated-artifact audit, and `git diff --check` successfully.
- The staging receipt records `passed`, zero issues, Hugo 0.166.0, and `checkedAt: 2026-10-04T00:14:35.224206+00:00` (October 3 locally). It names revision `e84ddd97bebc67154a0bb255e27fa86dbcad2b86` with `workingTreeDirty: true`, covering the uncommitted corrections through its source hashes.

Codex read Ryan’s terminal results and the generated report; it did not run tests, builds or GitNexus analysis. Documentation-only status updates followed the successful checks. Browser, physical-device, professional field and live-provider acceptance remain separate.

For future implementation changes, the complete verification command is:

```sh
bash scripts/verify-local.sh
```

Requires Hugo Extended 0.166.0, Node 22 (including `node:sqlite`), and the Python dependencies in `requirements.txt`. The script chooses `.venv/bin/python` when present and explains dependency setup if unavailable. It runs Python and Node regressions, checks the feature documentation, performs the temporary subpath staging build/audit, and checks diff whitespace. It does not deploy, send inquiries, call live providers or rebuild GitNexus. Tests create disposable Git repositories and synthetic approvals only inside temporary fixtures.

Coverage now includes rendered inquiry choices against the shared schema, every supported barn-door option, local runtime service IDs against the catalog, starting-point/date persistence, storage readback, receipt idempotency, immutable retry behavior, survey parsing/import/arithmetic, operator query boundaries, clean production provenance and output manifest hashes. UI mocks and generated markup checks are not real-browser evidence.

The staging report is `/tmp/jeff-does-doors-preview-report.json`; this temporary file can be overwritten by a later run. A production build should remain blocked in the current real checkout: contacts, coverage, source approvals and production URL are unresolved, and the latest corrections are uncommitted.

## Browser and field acceptance

- At narrow/mobile widths, the hero text/action appears before the image; no horizontal page overflow. FAQ jump label remains readable; the comparison region scrolls with keyboard focus.
- At 200%/400% zoom and with reduced motion, traverse navigation, brief optional fields, errors and results. Confirm announcements and focus with the intended screen reader.
- Exercise every brief choice, optional target date, restore/delete and denied storage. Confirm starting point and date in exported and received versions when online sending is deliberately configured.
- Verify direct email/SMS recipients and text on actual devices. Long messages must instruct copying/pasting rather than silently lose part of the message. A handoff is not a receipt.
- Survey: enter an inch fraction, convert to millimetres and back, change weight units, leave dimensions unknown, and record an insufficient width/headroom/capacity. No case should imply installation approval.
- Survey: export JSON, change fields, import the saved file, reject a malformed/oversized file, cancel replacement, and change fields while a file loads. Current work must remain when an import is rejected.
- Survey: save/restore/delete, start another opening, expire storage, deny clipboard/storage, download text and print. Check that print contains the packet rather than the form/navigation. Device copy and downloaded copies have separate lifetimes.
- Survey: complete one real opening with a professional using the actual manual. Check datum meanings, dimensions, materials/scope, unresolved checks and customer handover needs.
- No JavaScript: navigation and content work; interactive buttons stay disabled and explain their requirement.

## Provider and release acceptance

The existing GitHub Pages workflow deploys staging on authorized pushes to `main` or manual dispatch. The separate PR workflow validates with read-only permissions. Repository configuration is not proof that either workflow has run remotely.

Cloudflare Functions/D1/Turnstile/Email acceptance remains separate. Exercise confirmed receipt, lost acknowledgment, wrong identity, notification failure/recovery, lead status changes and retention against explicitly selected test resources. Verify actual HTTP headers on the chosen host; `_headers` is a Cloudflare mechanism and does not configure GitHub Pages headers.

After explicit release authorization, review pending sources and real business evidence, commit the intended revision, build with the production release gate and deploy the exact audited output. Source/output SHA-256 maps identify bytes; they do not constitute signatures or proof of hosting, delivery, accessibility conformance or physical installation suitability.
