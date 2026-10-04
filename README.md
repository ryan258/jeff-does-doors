# Jeff Does Doors

A local Hugo website draft for Jeff Does Doors, adapted from a reusable construction master that lives in its own repository. Ryan confirmed that Jeff specializes in barn-style doors. The creative direction interprets this as interior sliding barn doors; exact supply, fabrication, installation, and repair arrangements await Jeff’s confirmation.

> **Parody copy.** The site text, customers, reviews, stats, and crew are invented for a joke version of the site. The real, owner-facing draft copy is in git history (commit `cdfe44c` and earlier). Jeff's real contact details, services, prices, and credentials are still unconfirmed.

## Preview

Requires Hugo Extended (verified with 0.166.0). From this directory:

```sh
bash scripts/preview.sh
```

Open <http://localhost:1317/>. The site uses the selected client features, noindex review configuration, and no online inquiry delivery. This command does not publish anything.

## Current site

- Home: “A door is part of the room.” (mid-century modern redesign)
- Four proposed project pages: barn-door installation, replacement/upgrades, tracks/hardware, and adjustments; service index features catalog imagery and project highlights.
- About, service area, FAQs, contact, privacy, preview terms, and accessibility.
- Architectural guidance components: four-point measuring & clearance guide, three-point photo prep checklist, door mechanism comparison table (sliding vs. pocket vs. hinged), and craft standards.
- Local project-message builder with service-specific prompts, copy/download, and optional seven-day device saving.
- Barn-door brand mark, favicon, and a complete suite of 14 optimized WebP images (hero, 4 services, about workshop, 7 gallery door styles, and dark timber CSS background texture); all identified as illustrative concepts in [imagery docs](docs/imagery.md).
- Updated `data/gallery.yaml` with 12 barn-door records, category tags (Pantry, Rustic, Double doors, Modern, Hardware, Craftsman, Custom, Bypass, Chevron, Glass, Mirrored), and AI concept disclosures.
- Expanded `data/faqs.yaml` addressing clearances & fit, hardware mechanics, and material/finish considerations.
- Generated site is responsive, lightweight, and cleanly audited.

See [the project roadmap](roadmap.md) for milestone tracking.

The source master is unchanged. No Git history, credentials, deployment workflows, or approvals were copied.

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
