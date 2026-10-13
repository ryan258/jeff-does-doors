# Verification and remaining acceptance

## Final expansion review and local commit scope — October 13, 2026

Reviewed the six new partials, shared styling, guide data, page wrapper, six visitor placements, regression fixtures, documentation and Git state. No functional blocker was found in that bounded review. One regression weakness was corrected: the nested-text escaping assertion previously searched the entire guide, where the escaped example JSON could mask unsafe specimen rendering. Each of the six repeated specimens now receives hostile nested text and has its actual preview checked independently for escaped text and absence of executable tags. These strengthened cases have not been executed by the agent.

A fresh staging compilation produced 26 pages under `/subpath/` with warnings treated as failures. Focused source and generated-artifact audits returned zero issues, and changed Python files parsed successfully. The six visitor placements were rechecked at 320px: no page overflow, duplicate IDs, unresolved heading/hint references, unexpected form controls or clipped non-table content were found. The FAQ document register received a fresh visual spot check. Earlier desktop and keyboard observations above still describe the unchanged rendering code.

The local commit groups are reusable components and guide coverage; visitor integration and its coverage; then reconciled documentation. Automated suite execution remains owner-run with `bash scripts/verify-local.sh`. No submodules or tracked Git links are present. Push, deployment and publication are outside this batch.

## Project-paperwork visitor integration — October 13, 2026

All 24 contractor components now have placements across 12 visitor routes; the living guide retains 34 specimens. The six additions appear on installation, replacement, hardware, adjustments, Contact, and FAQ. Page-specific copy remains independent of guide fixtures, and actual work, orders, visits and acceptance remain unconfirmed.

Observed checks for this integration:

- Hugo 0.166.0 Extended compiled 26 pages with `--panicOnWarning` under `/subpath/`. Focused staging source and generated-artifact audits returned zero issues.
- Chrome emulation at 320px showed document width equal to viewport width on all six changed visitor routes. All six received visual spot checks, with no clipped new headings, record text or actions outside the intentional table scroll areas. Installation and Contact also received visual checks at 1440px, with no page overflow.
- Both new tables retained contained scroll regions (286px viewport, 620px table), and ArrowRight moved each 40px while focused. Status labels and record facts stack on narrow screens; Contact access areas become one column and FAQ document statuses wrap below the description.
- The guide rendered 24 actual-placement links, including the six new destinations, without duplicate IDs. Generated feature documentation, changed Python syntax and diff whitespace checks passed. GitNexus change analysis reported low risk with no partial/truncated result; source and browser review supplement its limited Hugo caller coverage.
- Regression coverage now expects all 24 placements and guide links, preserves service placements without catalogue data, and checks read-only records, keyboard table regions, form-first ordering and the real survey link. Tests were authored, not executed by the agent. Run `bash scripts/verify-local.sh` for the current revision.

The integration reuses the shared responsive component styles and adds no scripts or persistence. These observations do not establish real-device, browser-zoom, no-JavaScript or assistive-technology acceptance. Local review and commit authorization do not include pushing or deployment.

## Earlier component inventory expansion — October 13, 2026

Ryan refreshed GitNexus before this pass. The index matched `f2c5df1` (224 files, 1,017 nodes, 2,220 edges, 36 processes). The existing 28-specimen catalogue received a source and mobile browser review; no blocker was found in that bounded review. The expansion adds six read-only project-paperwork patterns, bringing the guide to 34 specimens and 24 contractor components. At that stage, visitor integration covered 18 components across 12 routes; the later integration described above brings it to all 24.

The new owner-run cases cover repeated IDs, escaping, caption/header/hint semantics, read-only states, real document links and omitted actions, and reuse through the existing page wrapper without new scripts. The agent has not run the automated tests. Earlier passing results below apply only to the revisions described.

Observed checks for the expansion:

- Hugo 0.166.0 Extended compiled 26 pages with `--panicOnWarning` at a `/subpath/` base URL. Staging source and generated-artifact audits returned zero issues.
- The browser rendered all 34 specimens without duplicate IDs at 390px. All six new previews had no out-of-viewport text or controls at 320px, excluding their intentional table scroll regions. The document-register mobile layout and site-access desktop layout received visual spot checks; document width matched the viewport at 320px, 390px and 1440px.
- ArrowRight moved the focused material table's horizontal scroll position. Searching “responsibility matrix” returned that specimen; reset restored all 34 entries and returned focus to search.
- Generated feature documentation, diff whitespace and changed Python syntax checks passed. Real device, browser zoom, no-JavaScript and assistive-technology acceptance remain separate.

## Earlier source review — October 13, 2026

The component library and site integration are implemented: 28 guide specimens, 18 contractor components across 12 visitor routes, mobile layout refinements, a sitewide character-copy pass and three native-disclosure Easter eggs. The final source review corrected FAQ clearance/delivery drift, aligned FAQ answer-source validation with rendering and regenerated the feature menu from corrected documentation text.

Evidence for this change set:

- Source review covered tracked changes and new components, scripts, datasets and regression files. GitNexus impact analysis was paired with direct source inspection where Hugo/data references or new files were unresolved. Graph results are not a substitute for runtime validation; the index was not rebuilt.
- The final local staging compilation passed with Hugo 0.166.0 Extended and `--panicOnWarning`, producing 26 pages under a `/subpath/` base URL. The staging source audit and generated-artifact audit each returned zero issues. Generated feature documentation matched its source, changed Python files parsed, and `git diff --check` passed. These are build/static checks, not execution of the automated suites or the full release command.
- The October 12 Chrome pass inspected all 12 integrated visitor routes at 320px for document width and clipped content, with visual spot checks at 320px or 390px and selected tablet/desktop checks. Home/Gallery choices, menu scrolling, contained comparison scrolling and the optional notes received bounded keyboard checks. The detailed observations are in [the component guide](component-library.md).
- A 200% root-font-size simulation was checked on the homepage. This is not full browser zoom, a real-device check or screen-reader acceptance.
- Ryan reported nine Python component-library tests and nine JavaScript choice tests passing before visitor integration. The later integration, copy, Easter-egg and review-fix coverage has been authored but not executed by the agent. The current complete suite is pending.
- No submodules or tracked Git links were found. Local commit authorization does not include a push or deployment.

## Historical owner results — October 3, 2026

**Owner-run automated verification passed after two corrections:** deprecated Hugo `site.Data` references were replaced with `hugo.Data`, and the search-ranking fixture was updated to query its barn-door title.

- Ryan’s full run passed all 24 Python tests, including the production-release fixtures.
- That run passed 46 of 47 Node tests; the sole failure was the stale search-ranking fixture. After its correction, Ryan’s targeted rerun passed both tests in `tests/brief-core.test.cjs`. All 47 Node cases therefore have passing evidence across these runs; this is not a claim of a subsequent single full-suite run.
- The follow-up command completed the feature-documentation check, staging source/generated-artifact audit, and `git diff --check` successfully.
- The staging receipt records `passed`, zero issues, Hugo 0.166.0, and `checkedAt: 2026-10-04T00:14:35.224206+00:00` (October 3 locally). It names revision `e84ddd97bebc67154a0bb255e27fa86dbcad2b86` with `workingTreeDirty: true`, covering the uncommitted corrections through its source hashes.

Codex read Ryan’s terminal results and the generated report; it did not run tests, builds or GitNexus analysis. Documentation-only status updates followed the successful checks. Browser, physical-device, professional field and live-provider acceptance remain separate.

## Current owner-run command

Run the complete verification against the current working tree, and retain which revision and local changes were checked:

```sh
bash scripts/verify-local.sh
```

Requires Hugo Extended 0.166.0, Node 22 (including `node:sqlite`), and the Python dependencies in `requirements.txt`. The script chooses `.venv/bin/python` when present and explains dependency setup if unavailable. It runs Python and Node regressions, checks the feature documentation, performs the temporary subpath staging build/audit, and checks diff whitespace. It does not deploy, send inquiries, call live providers or rebuild GitNexus. Tests create disposable Git repositories and synthetic approvals only inside temporary fixtures.

Existing foundation coverage includes rendered inquiry choices against the shared schema, every supported barn-door option, local runtime service IDs against the catalog, starting-point/date persistence, storage readback, receipt idempotency, immutable retry behavior, survey parsing/import/arithmetic, operator query boundaries, clean production provenance and output manifest hashes. UI mocks and generated markup checks are not real-browser evidence.

The new component tests add catalogue filtering and clipboard fallback, choice isolation and restored selection, escaped text, repeated-instance IDs, route placement, feature suppression, subpaths, source inventory and native-disclosure placement. Review-fix cases cover the shared FAQ guidance and delivery modes. These are authored expectations until the owner runs them.

The staging report is `/tmp/jeff-does-doors-preview-report.json`; this temporary file can be overwritten by a later run. A production build should remain blocked in the current real checkout: contacts, coverage, source approvals and production URL are unresolved. Creating local commits does not resolve those publication requirements.

## Browser and field acceptance

- At narrow/mobile widths, the hero text/action appears before the image; no horizontal page overflow. FAQ jump label remains readable; the comparison region scrolls with keyboard focus.
- At 200%/400% zoom and with reduced motion, traverse navigation, brief optional fields, errors and results. Confirm announcements and focus with the intended screen reader.
- Exercise every brief choice, optional target date, restore/delete and denied storage. Confirm starting point and date in exported and received versions when online sending is deliberately configured.
- Verify direct email/SMS recipients and text on actual devices. Long messages must instruct copying/pasting rather than silently lose part of the message. A handoff is not a receipt.
- Survey: enter an inch fraction, convert to millimetres and back, change weight units, leave dimensions unknown, and record an insufficient width/headroom/capacity. No case should imply installation approval.
- Survey: export JSON, change fields, import the saved file, reject a malformed/oversized file, cancel replacement, and change fields while a file loads. Current work must remain when an import is rejected.
- Survey: save/restore/delete, start another opening, expire storage, deny clipboard/storage, download text and print. Check that print contains the packet rather than the form/navigation. Device copy and downloaded copies have separate lifetimes.
- Survey: complete one real opening with a professional using the actual manual. Check datum meanings, dimensions, materials/scope, unresolved checks and customer handover needs.
- Guide and choices: search/filter/reset, direct specimen links, clipboard denial, arrow-key selection and independent instances. Verify checked radio, displayed panel, status text and focus agree.
- Easter eggs: all three start closed, open/close from the keyboard, keep focus on their summaries and remain outside forms and error recovery.
- No JavaScript: navigation and content remain readable; choice controls and guide filters stay hidden while all option panels/specimens remain visible. Native disclosures and checkboxes remain usable. Brief/survey enhancements explain their JavaScript requirement.

## Provider and release acceptance

The existing GitHub Pages workflow deploys staging on authorized pushes to `main` or manual dispatch. The separate PR workflow validates with read-only permissions. Repository configuration is not proof that either workflow has run remotely.

Cloudflare Functions/D1/Turnstile/Email acceptance remains separate. Exercise confirmed receipt, lost acknowledgment, wrong identity, notification failure/recovery, lead status changes and retention against explicitly selected test resources. Verify actual HTTP headers on the chosen host; `_headers` is a Cloudflare mechanism and does not configure GitHub Pages headers.

After explicit release authorization, review pending sources and real business evidence, commit the intended revision, build with the production release gate and deploy the exact audited output. Source/output SHA-256 maps identify bytes; they do not constitute signatures or proof of hosting, delivery, accessibility conformance or physical installation suitability.
