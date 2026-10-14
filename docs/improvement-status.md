# Current implementation and next actions

Updated October 13, 2026. This is the Jeff Does Doors parody preview, with a reusable contractor component library, a local single-opening survey workspace and an optional Cloudflare inquiry adapter. Contacts, coverage and fabrication scope remain unconfirmed. Online intake is disabled and the evidence register is empty.

**The October 12–13 component, mobile, copy, Easter-egg and paperwork integration work is implemented; the current complete automated run is still pending.** Source review found and corrected FAQ guidance/delivery drift and stale generated documentation. Local compilation and bounded browser observations are recorded in [verification](verification.md). Earlier owner-run test results remain dated evidence for their respective revisions.

## Current component and character work

| Area | Implemented state | Remaining check |
| --- | --- | --- |
| Living style guide | 42 real specimens: 32 contractor components, six shared patterns and four foundations; search, family filters, snippets, direct task links and live placement links | Current owner-run regressions; broader zoom, no-JavaScript and assistive-technology checks |
| Visitor integration | 24 contractor components across 12 routes, with independent copy and publication-source registration; eight enquiry-through-aftercare additions currently guide-only with wrapper support | Current placement, feature-suppression and subpath regressions |
| Mobile layout | Text-first hero, wrapping header, opaque menu, responsive choice panels, tables and quieter component surfaces; native 200%/400% checks cover the six paperwork patterns | Real devices and wider workflow zoom checks |
| Character copy | Distinct Jeff, Doreen and Lenny voices; shorter service copy; fictional reviews and unresolved terms disclosed | Editorial review whenever examples become real business content |
| Easter eggs | Three closed native disclosures on Home, Gallery and About; no script or stored preference | No-JavaScript and screen-reader acceptance |
| FAQ guidance | Four clearance answers resolve the same product-specific guidance as the measuring cards; universal dimensions removed | Actual selected-product review and authored regression coverage |
| Delivery wording | Brief help, Contact and delivery FAQ use the configured delivery-state partial | Authored local/contact/online fixture coverage; provider acceptance remains separate |
| Source validation | FAQ policy accepts text, supported guidance references or boolean delivery-state answers; malformed sources are rejected | Owner-run policy regressions |
| Documentation | README, roadmap, architecture, component guide, status and verification records reflect the 42-specimen / 32-contractor-component expansion | Keep results tied to the revision actually checked |
| Homepage concept spread | Four architectural concept studies (`#next-openings`) on Home; uncropped 3:2 layout, 480/960/1536 responsive WebP variants, explicit AI disclosures, direct links without lightbox | Placement, subpath resolution and publication inventory regressions in `tests/test_next_openings.py` |
| Brief & survey zoom/focus | Aligned brief result scroll start, survey packet heading focus, explicit action error status reveal with field preservation | Native 200%/400% zoom checks; authored UI tests in `tests/survey-ui.test.cjs` |

The subsequent inventory expansion adds six read-only project-paperwork patterns: decisions, responsibilities, site access, materials, open items and document references. All appear in the living guide and now have visitor placements: installation responsibilities, replacement decisions, hardware materials, adjustment open items, Contact access planning, and FAQ document references. The six affected pages received 320px visual checks; both new tables retain contained keyboard scrolling. The refreshed GitNexus index matched the latest local commit at the start of this pass. New coverage remains owner-run.

The enquiry-through-aftercare guide expansion adds eight reusable contractor patterns: enquiry summary, site observations, permission tracker, disruption plan, estimate breakdown, payment milestones, removal/reuse plan, and product care guide. All eight render as live specimens in the style guide with fictional character copy, contracts, snippets, direct task links, and responsive styling. They currently have guide placements only, with wrapper support in `layouts/partials/site-component.html` for future reuse. The estimate provides an accessible keyboard-scrollable table region with scoped headers, care disclosures use native details/summary starting closed, and amounts and terms remain unresolved. Authored regression coverage in `tests/test_contractor_expansion.py` covers live specimen discovery, HTML escaping, empty states, repeated IDs/ARIA resolution, table semantics, native care disclosures, link pairs, and wrapper reuse.

The subsequent native keyboard/zoom pass corrected Message-bar overlap of focused links at 400% and cramped table status columns. The bar now follows the footer on short viewports; taller phone views reserve focus-scroll clearance. These local CSS follow-ups do not change publication or deployment readiness. See the manual regression checklist in [verification](verification.md).

The brief/survey follow-up now aligns the brief result start, focuses the survey packet heading, and reveals explicit survey action errors. Native Chrome 200%/400% observations cover the current single-page workflows, with bounded keyboard and download checks. Save/restore, re-import, clipboard contents, print and assistive-technology acceptance remain open; see [verification](verification.md). New survey focus regression cases are authored but not agent-run.

The homepage concept spread ("The next opening") introduces four architectural concept studies (sculpted oak slider, amber reeded glass panels, folding walnut screen, and terrazzo-inspired quiet pivot) on Home between styles and catalog. The partial renders uncropped 3:2 responsive WebP images with 480w, 960w, and 1536w variants, explicit dimensions, and native full-image links without lightbox or JavaScript dependencies. Prompts, dimensions, and provenance are recorded in [imagery docs](imagery.md). Authored regressions in `tests/test_next_openings.py` cover placement with the gallery disabled, accessibility labels and disclosures, subpath destinations, and publication inventory registration.

## Existing foundation

The earlier implementation includes the shared inquiry schema, starting-point and target-date capture, optional seven-day device drafts with readback, receipt-bound optional intake, the survey packet, the bounded operator helper, PR validation and revision-bound release receipts. October 3 owner results cover that earlier work; they are not a fresh pass for this component revision.

The broad preview intentionally renders fictional crew, reviews and other optional content. A business launch would use its own reviewed feature selection and actual evidence. Legacy dataset display flags do not make the parody factual or populate the evidence register.

## Professional workflow delivered

One packet represents one opening. Measurements accept decimal inches, inch fractions, or millimetres. Unit changes convert existing dimensions; weight units convert independently. Width, headroom and maximum-weight comparisons show the entered assumptions and unresolved values. Pair/bypass arrangements disable single-door calculations. No generic overlap, floor gap, capacity or mounting height is silently supplied.

The packet includes supply responsibility, scope/exclusions, materials/order notes, estimate reference, changes, installation observations and handover. The user can export editable JSON, import a validated packet, download text, copy or print. Saving is opt-in, scoped to this business/site path, with a seven-day expiry on next access. Import and new-opening actions protect existing work with explicit replacement prompts. Nothing is sent to the business by the survey.

The current packet has one opening and free-text materials/estimate records. It is not a quoting engine, multi-job database, manufacturer compatibility catalog, structural calculator or signed acceptance record.

## Next actions, in order

1. Run `bash scripts/verify-local.sh` against the current working tree and review its results. The agent has not run the automated suites.
2. Trial one real opening: measurements, manual revision, export/re-import, print and handover checklist. Keep observed friction and missing fields in the packet.
3. Complete browser/assistive-technology checks in `docs/verification.md`.
4. If proceeding to a business launch, confirm supply/fabrication/installation scope, contacts and coverage; supply authentic photography, approved copy and actual terms. Record exact revision approval; do not turn parody into asserted facts.
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

Business facts, field acceptance, production configuration and publishing need their own evidence. Ryan’s earlier local review and documentation batches were committed. The enquiry-through-aftercare guide expansion, docs, and regression coverage have now received source review and local commit authorization. No submodules are present.
