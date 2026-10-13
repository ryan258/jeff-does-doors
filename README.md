# Jeff Does Doors

A local Hugo website and door-survey workspace for Jeff Does Doors, adapted from a reusable construction master that lives in its own repository. Ryan confirmed that Jeff specializes in barn-style doors. The creative direction interprets this as interior sliding barn doors; exact supply, fabrication, installation, and repair arrangements await Jeff’s confirmation.

> **Parody copy.** The site text, customers, reviews, stats, and crew are invented for a joke version of the site. The real, owner-facing draft copy is in git history (commit `cdfe44c` and earlier). Jeff's real contact details, services, prices, and credentials are still unconfirmed.

## Preview

Requires Hugo Extended (verified with 0.166.0). From this directory:

```sh
./jdd.sh
```

Open <http://localhost:1317/> for the website or <http://localhost:1317/survey/> for the door survey. Keep the terminal open and press **Ctrl+C** to stop. The launcher checks for Hugo Extended and delegates to `scripts/preview.sh`; no dependency installation, tests or re-indexing run automatically. Use `./jdd.sh --help` for a reminder.

The [component living style guide](http://localhost:1317/style-guide/) contains 34 rendered specimens: twenty-four reusable contractor components, six existing shared patterns, and four theme foundations. The field-office edition adds interactive project/finish choices, package comparisons, crew cards, a featured quote, field notes, change summaries, and follow-up plans—with Jeff, Doreen, and Lenny continuing the parody. Search the catalogue (including character copy), inspect states, and copy the Hugo usage snippets. It is a review-only page; production uses the existing disabled-page guard. See [the component integration guide](docs/component-library.md) for contracts and the source map.

All twenty-four contractor components are used across twelve visitor-facing routes: Home, the four service pages, Gallery, About, Pricing, Contact, Service Area, FAQ, and Reviews. The guide links each specimen to its page section. Page-specific copy lives in `data/site_components.json`, independently of the guide fixtures, and participates in the publication source inventory. Jeff has acquired a door-birthday anecdote; Doreen has acquired more paperwork; Lenny remains a level.

The project-paperwork expansion adds a decision register, responsibility matrix, site-access plan, material schedule, punch list, and document register. These six now appear on the four service pages, Contact, and FAQ, with concise page-specific planning copy. They keep responsibilities, product choices, access, open items, and document references explicit without inventing assignments or completed work. No new JavaScript, storage, purchasing, scheduling, or approval behavior is added.

Three optional character notes reward a closer look: Lenny in the homepage footer, Jeff after the Gallery grid, and Doreen inside her clipboard on About. They are closed native disclosures, with no script or saved state. The mobile layouts, page copy, and component styling have also been revised together; the jokes stay outside task controls and delivery feedback.

The preview binds to this computer (`127.0.0.1`) and uses the selected client features, noindex review configuration, and no online inquiry delivery. This command does not publish anything. The existing `bash scripts/preview.sh` command remains available.

## Current site

- Home: “The room is there for the door.” (mid-century modern design, with text and actions before the image on mobile)
- Home “The next opening” concept spread: four large AI-generated images of a sculpted oak slider, amber glass panels, a folding walnut screen, and a terrazzo-inspired pivot. Responsive images and native full-image links; clearly labeled as concepts rather than completed projects or available products.
- Four proposed project pages: barn-door installation, replacement/upgrades, tracks/hardware, and adjustments; service index features catalog imagery and project highlights.
- About, service area, FAQs, contact, privacy, website terms, and accessibility.
- Architectural guidance components: four-point measuring & clearance guide, three-point photo prep checklist, door mechanism comparison table (sliding vs. pocket vs. hinged), and craft standards.
- Local project-message builder with service-specific prompts, copy/download, and optional seven-day device saving.
- Barn-door brand mark, favicon, and 26 optimized WebP images (14 base site/gallery assets plus 12 responsive concept variants across three sizes); all identified as illustrative concepts in [imagery docs](docs/imagery.md).
- Updated `data/gallery.yaml` with 12 barn-door records, category tags (Pantry, Rustic, Double doors, Modern, Hardware, Craftsman, Custom, Bypass, Chevron, Glass, Mirrored), and AI concept disclosures.
- Expanded `data/faqs.yaml` addressing clearances & fit, hardware mechanics, and material/finish considerations.
- A single-opening survey workspace at `/survey/`: inch/fraction or metric measurements, hardware references, scope and materials, installation checks, handover notes, optional device saving, JSON import/export, text download, copy and print.
- October 12 implementation and October 13 review: source and dependency review, successful local staging compilation, and bounded browser checks of the component/mobile/copy work. Ryan previously reported nine component-library Python tests and nine choice JavaScript tests passing before page integration. The current complete regression run remains owner-run and pending; see [the verification record](docs/verification.md) for the separate historical results and remaining acceptance.

See [the project roadmap](roadmap.md) for milestone tracking.

The source master is unchanged. This repository has its own GitHub Pages staging deployment workflow and a separate pull-request validation workflow. Cloudflare production activation and business approvals remain pending.

## Editing map

| Source | Responsibility |
| --- | --- |
| `profiles/jeff-does-doors.toml` | Identity, contacts, coverage, hero |
| `data/specialties.yaml` | Barn-door homepage positioning |
| `data/services.yaml` and `content/services/` | Proposed catalog, detail pages, and service index highlights |
| `data/gallery.yaml` | Barn door gallery dataset (12 styles and hardware entries) |
| `data/faqs.yaml`, `data/process.yaml` | Questions, clearances, mechanics, and project-planning steps |
| `layouts/index.html` | Homepage copy and sections |
| `data/next_openings.json`, `layouts/partials/next-openings.html`, `assets/scss/_next-openings.scss` | Next-generation concept imagery, captions, and responsive homepage spread |
| `layouts/partials/` | Architectural partials: measuring guide, photo prep, door comparison, craft standards |
| `data/component_library.json`, `layouts/_default/style-guide.html` | Review catalogue, fixtures, source contracts and live specimen links |
| `data/site_components.json`, `layouts/partials/site-component.html` | Visitor-page component copy, placement metadata and feature-aware wrapper |
| `layouts/partials/components/`, `assets/scss/_contractor.scss` | Twenty-four reusable components and responsive presentation |
| `assets/js/contractor-choices.js`, `assets/js/style-guide.js` | Independent choice controls and guide-only filtering/clipboard behavior |
| `layouts/partials/easter-egg.html`, `assets/scss/_easter-eggs.scss` | Three optional Jeff-profile character notes |
| `assets/scss/_modern.scss` | Modern design system, component layouts, and responsive styling |
| `assets/scss/_doors.scss` | Client refinements & CSS wood texture overlays over shared foundations |
| `hugo.toml`, `hugo-launch.toml` | Broad parody preview defaults and a separate minimal launch selection |
| `assets/contracts/brief-schema.json` | Shared Hugo/browser/server inquiry choices and limits |
| `data/door-guidance.json`, `layouts/partials/faq-answer.html` | Shared product-specific measurement guidance and FAQ answer resolution |
| `layouts/partials/delivery-status.html` | Capability-aware help used by the brief, contact page and delivery FAQ |
| `assets/contracts/survey-schema.json`, `assets/js/survey-core.mjs`, `assets/js/survey.js` | Survey fields, calculations, file boundary, device storage and UI |
| `scripts/lead_desk.py` | Bounded D1 operator commands and notification retry |
| `data/evidence.json` | Revision-bound approvals, currently empty |

Start with [the review and restart note](docs/jeff-review.md), [current status](docs/improvement-status.md), and [roadmap](roadmap.md).


## Focused validation

Set up Python dependencies if needed:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run the selected-profile staging audit:

```sh
.venv/bin/python scripts/release_check.py --staging --base-url https://fixture-review.org/jeff-does-doors/ --report /tmp/jeff-preview-report.json
```

This builds and audits temporary local output. It does not contact that URL or deploy.

For every gate at once:

```sh
bash scripts/verify-local.sh
```

Browser acceptance and business approval remain separate. See [verification](docs/verification.md).

Before launch, confirm services, who supplies/builds the doors, territory, contacts, business introduction, photos, policies, domain, and hosting. The existing production approval gate remains intact.
