# Current implementation and next actions

Updated October 3, 2026. This is one Hugo site for Jeff Does Doors, with a local single-opening survey workspace and an optional Cloudflare inquiry adapter. The selected profile still has no confirmed business contact details, coverage or fabrication scope. Online intake remains disabled.

**Owner-run automated verification passed after the Hugo API and search-fixture corrections.** Ryan’s full run passed 24 Python tests and 46 of 47 Node tests; the corrected two-test search file then passed its targeted rerun. The follow-up documentation check, staging source/artifact audit and whitespace check also passed. These are combined results across runs, not a new single full-suite run. Codex did not execute tests, builds or re-indexing. See [verification](verification.md) for the receipt and remaining acceptance boundaries.

## Review findings and solutions

| Finding | Implemented response | Remaining acceptance |
| --- | --- | --- |
| Eight visible intake choices disagreed with the server | `assets/contracts/brief-schema.json` now supplies rendered options, validation limits and friendly field labels; current barn-door fixtures cover every choice | Automated checks passed; optional provider acceptance remains |
| Starting point was dropped online | Included in normalized payload, canonical hash and saved D1 payload | Automated persistence check passed; live-provider acceptance remains |
| Target-date choice had no actual date | Optional date input, shared validation, local draft recovery and brief output | Real browser entry/restore |
| Form limits and errors were inconsistent | Name/contact limits match the contract; readable field names; rendered-form contract assertions | Browser error focus and screen-reader announcement |
| Universal clearance and material claims were unsupported | Shared measurement guidance uses explicit datums and exact product manuals; comparison, craft and FAQ copy is conditional | Professional review with the actual selected systems |
| Photos were described as verifying clearances | Photo guidance now supports survey planning, not dimensional or structural approval | Real photo/measurement workflow |
| FAQ navigation label had insufficient contrast | Dedicated dark-on-light label with readable size | Browser contrast/zoom confirmation |
| Comparison overflow lacked keyboard access | Labelled, focusable scrolling region | Keyboard and touch verification |
| Preview messages contradicted enabled capabilities | Shared delivery-status partial used by form, contact, FAQ and review notice; terms/privacy updated | Check direct-contact and online modes in configured fixtures |
| Hero CTA implied completed work | “Explore door ideas”; illustrative disclosure retained | Replace with authentic approved job media when available |
| Mobile image preceded the primary action | Copy/action precedes the image at narrow widths; image height is bounded | Real mobile viewport check |
| Social metadata and Markdown images drifted from visible imagery | Specialty hero fallback shared with metadata; Markdown images use responsive image partial | Generated asset checks passed; actual social preview remains |
| Long mail/SMS links risked truncation | Long messages open the app without the body and tell users to paste the copied brief | Real iOS/Android mail/SMS checks |
| Browser save could claim success without readback | Saved brief now verifies the stored bytes; one-draft replacement is explained | Automated storage checks passed; real-browser storage/restore remains |
| No professional job workflow | `/survey/` records job/opening, datums, dimensions, hardware/manual, scope, materials, estimate notes, checks and handover; produces a reusable packet | Field trial with a barn-door professional |
| Raw SQL was the only operator interface | `lead_desk.py` lists receipt metadata, shows a selected inquiry, previews status changes and supports explicit notification retry | Configured local/provider acceptance; no live use performed |
| PR checks were claimed but absent | Dedicated read-only PR validation workflow added; existing push/manual staging deploy remains separate | Actual GitHub run after an authorized push |
| Dirty production tree could produce a misleading revision receipt | Production requires clean Git state; receipt includes source and output hashes and checks for source changes during build | Owner-run production fixture tests passed; actual production remains blocked |
| Release controls escaped source review | Scripts, workflow files, dependency requirements and new schemas join the approval inventory | Real approvals remain empty |
| Hash records were called signatures | Docs and receipt explicitly distinguish hashes from digital signatures; review inventory can list pending sources by technical/business area | Owner process and repository protections |
| Hugo warnings could be overlooked | Release builds use `--panicOnWarning`; all 12 new deprecated data references were corrected | Owner-run staging gate passed with warnings treated as failures |
| Disabled modules contained excavation copy and invented numbers | Door-specific unconfirmed placeholders; no fake statistics, active promotions, hiring or payment claims | Keep modules disabled until their actual facts are supplied |
| Tests and documentation reflected a different trade or revision | Barn-door fixtures, rendered-option contract checks, survey and operator regressions; stale search query corrected and results recorded | Automated checks passed across the full run and targeted follow-up |

## Professional workflow delivered

One packet represents one opening. Measurements accept decimal inches, inch fractions, or millimetres. Unit changes convert existing dimensions; weight units convert independently. Width, headroom and maximum-weight comparisons show the entered assumptions and unresolved values. Pair/bypass arrangements disable single-door calculations. No generic overlap, floor gap, capacity or mounting height is silently supplied.

The packet includes supply responsibility, scope/exclusions, materials/order notes, estimate reference, changes, installation observations and handover. The user can export editable JSON, import a validated packet, download text, copy or print. Saving is opt-in, scoped to this business/site path, with a seven-day expiry on next access. Import and new-opening actions protect existing work with explicit replacement prompts. Nothing is sent to the business by the survey.

The current packet has one opening and free-text materials/estimate records. It is not a quoting engine, multi-job database, manufacturer compatibility catalog, structural calculator or signed acceptance record.

## Next actions, in order

1. Confirm Jeff’s supply/fabrication/installation scope, then contact details and coverage. The unanswered scope question stays unknown.
2. Trial one real opening: measurements, manual revision, export/re-import, print and handover checklist. Keep observed friction and missing fields in the packet.
3. Complete browser/assistive-technology checks in `docs/verification.md`.
4. Supply authentic photography, approved service copy and actual commercial terms. Record exact revision approval; do not turn placeholders into asserted facts.
5. Choose and authorize the operational host and receiving workflow. Configure and prove provider delivery separately before enabling intake.

## Remaining enhancement proposals

| Opportunity | Proposed solution | Dependency / acceptance |
| --- | --- | --- |
| Several openings and repeat jobs | Versioned job collection with opening IDs, named local records and transactional import/export | First field trial; migration/recovery tests |
| Structured takeoff and estimating | Line items with quantities, labor, supplier quote date, taxes/allowances and explicit exclusions | Jeff’s actual estimating method; no invented rates |
| Hardware selection | Curated maker/model catalog with manual URL/revision, verified limits and freshness owner | Manufacturer sources and maintainer commitment |
| Photo evidence | Local attachments with labels, consent, size limits and export manifest | Photo handling/retention decision |
| Measured drawings | Dimensioned elevation and travel diagram using the packet datums | Real single-opening workflow validation |
| Customer handover package | Branded packet with care instructions, product manuals, outstanding items and acknowledgment | Approved terms and real installation evidence |
| Operator inbox | Authenticated accessible list/detail UI over the existing receipt/status model | Identity/access and provider decision |
| Submitted-revision recovery across reload | Separate explicit opt-in saved submission snapshot bound to UUID/hash, with expiry | Privacy copy and dedicated retry/reload tests; current automatic storage remains metadata-only |
| CSS/JS maintenance | Gradually split the legacy optional-feature handlers and retire superseded styles; load only needed modules | Baseline screenshots and browser behavior checks first |
| Repeatable accessibility evidence | Bounded keyboard/zoom/screen-reader cases around forms, file import, storage and print | Actual assistive-technology use |

Business facts, field acceptance, production configuration and publishing need their own evidence. No files have been staged, committed, pushed or deployed by this implementation.
