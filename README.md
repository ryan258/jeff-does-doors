# Jeff Does Doors

A local Hugo website and door-survey workspace for Jeff Does Doors, adapted from a reusable construction master that lives in its own repository. Ryan confirmed that Jeff specializes in barn-style doors. The creative direction interprets this as interior sliding barn doors; exact supply, fabrication, installation, and repair arrangements await Jeff’s confirmation.

> **Parody copy.** The site text, customers, reviews, stats, and crew are invented for a joke version of the site. The real, owner-facing draft copy is in git history (commit `cdfe44c` and earlier). Jeff's real contact details, services, prices, and credentials are still unconfirmed.

## Preview

Requires Hugo Extended (verified with 0.166.0). From this directory:

```sh
./jdd.sh
```

Open <http://localhost:1317/> for the website or <http://localhost:1317/survey/> for the door survey. Keep the terminal open and press **Ctrl+C** to stop. The launcher checks for Hugo Extended and delegates to `scripts/preview.sh`; no dependency installation, tests or re-indexing run automatically. Use `./jdd.sh --help` for a reminder.

The preview binds to this computer (`127.0.0.1`) and uses the selected client features, noindex review configuration, and no online inquiry delivery. This command does not publish anything. The existing `bash scripts/preview.sh` command remains available.

## Current site

- Home: “A door is part of the room.” (mid-century modern redesign)
- Four proposed project pages: barn-door installation, replacement/upgrades, tracks/hardware, and adjustments; service index features catalog imagery and project highlights.
- About, service area, FAQs, contact, privacy, website terms, and accessibility.
- Architectural guidance components: four-point measuring & clearance guide, three-point photo prep checklist, door mechanism comparison table (sliding vs. pocket vs. hinged), and craft standards.
- Local project-message builder with service-specific prompts, copy/download, and optional seven-day device saving.
- Barn-door brand mark, favicon, and a complete suite of 14 optimized WebP images (hero, 4 services, about workshop, 7 gallery door styles, and dark timber CSS background texture); all identified as illustrative concepts in [imagery docs](docs/imagery.md).
- Updated `data/gallery.yaml` with 12 barn-door records, category tags (Pantry, Rustic, Double doors, Modern, Hardware, Craftsman, Custom, Bypass, Chevron, Glass, Mirrored), and AI concept disclosures.
- Expanded `data/faqs.yaml` addressing clearances & fit, hardware mechanics, and material/finish considerations.
- A single-opening survey workspace at `/survey/`: inch/fraction or metric measurements, hardware references, scope and materials, installation checks, handover notes, optional device saving, JSON import/export, text download, copy and print.
- October 3 automated checks passed in Ryan’s full run and targeted follow-up after two corrections. Browser, field and provider acceptance remain open; see [the verification record](docs/verification.md).

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
| `layouts/partials/` | Architectural partials: measuring guide, photo prep, door comparison, craft standards |
| `assets/scss/_modern.scss` | Modern design system, component layouts, and responsive styling |
| `assets/scss/_doors.scss` | Client refinements & CSS wood texture overlays over shared foundations |
| `hugo.toml`, `hugo-launch.toml` | Matching minimal feature selections |
| `assets/contracts/brief-schema.json` | Shared Hugo/browser/server inquiry choices and limits |
| `data/door-guidance.json` | Shared measurement guidance for homepage and FAQ |
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
