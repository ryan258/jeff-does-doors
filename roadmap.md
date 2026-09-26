# Jeff Does Doors — Project Roadmap

A milestone plan for taking the **Jeff Does Doors** local website draft from foundational concept to an owner-approved, production-ready web presence.

---

## Phase 1: Foundation & Specialty Adaptation (Completed)

- [x] **Client Specialty Definition**: Adapted the site architecture around Jeff's specialty in interior barn-style sliding doors.
- [x] **Service Catalog**: Designed four core service offerings:
  1. Barn-door installation (`barn-door-installation`)
  2. Door replacements & upgrades (`barn-door-replacement`)
  3. Tracks, pulls & hardware (`tracks-hardware`)
  4. Barn-door adjustments (`barn-door-adjustments`)
- [x] **Client Branding & Palette**: Established amber/woodcraft tone, bespoke barn door SVG logo mark, and favicon.
- [x] **Inquiry Builder & Safety Gate**: Implemented client-side project message builder without silent submission; hardened intake policy tests.
- [x] **Factory Cleanup**: Removed inherited multi-tenant CLI tooling and excess demonstration profiles to maintain a clean single-client codebase.

---

## Phase 2: Visual & Media Flesh-Out (Completed)

- [x] **High-Resolution WebP Suite**: Generated 9 optimized WebP assets tailored to architectural door work:
  - Hero image: `images/barn-door-illustration.webp` (natural oak sliding door)
  - Service 01: `images/barn-door-pantry.webp` (modern white shaker slider)
  - Service 02: `images/barn-door-walnut.webp` (dark walnut X-brace slider)
  - Service 03: `images/barn-door-hardware.webp` (macro spoke roller & steel track detail)
  - Service 04: `images/barn-door-floor-guide.webp` (adjustable bottom floor guide & mortise)
  - Gallery 01: `images/barn-door-french-glass.webp` (double French divided-lite glass sliders)
  - Gallery 02: `images/barn-door-oak-slab.webp` (minimalist rift-cut white oak slab)
  - Gallery 03: `images/barn-door-craftsman.webp` (warm amber Craftsman panel door)
  - About / Craft: `images/barn-door-workshop.webp` (artisan workbench with hand plane & track hardware)
- [x] **CSS Background Integration**: Generated `images/wood-texture-dark.webp` and integrated subtle timber grain overlays in `_doors.scss` for `.cta-banner`, `.approach`, and hero blocks.
- [x] **Gallery Data Replacement**: Replaced all inherited excavation/septic placeholders in `data/gallery.yaml` with authentic door entries, tags, and AI concept disclosure alt-texts.
- [x] **Prose Image Integration**: Embedded illustrative visuals across service markdown files and `/about`.
- [x] **Documentation & Provenance**: Recorded prompt records, dimensions, and `.attic/` source archives in `docs/imagery.md`.

---

## Phase 3: Owner Discovery & Business Intake (Next Action)

- [ ] **Core Business Questions with Jeff**:
  - Does Jeff build/fabricate doors, install customer-supplied doors, or both?
  - Does he offer swing-to-slide conversions and tune-up/adjustment services?
- [ ] **Contact & Operational Details**:
  - Confirmed business phone, SMS support, email, and response turnaround.
  - Confirmed physical address or service-area radius (counties and towns served).
  - Business hours and intake routing.
- [ ] **Owner Story & About Content**:
  - Jeff's background, woodworking journey, and customer philosophy for `/about`.
- [ ] **Real Job Photography**:
  - Replace illustrative AI concept images with real photos of completed installations, tracks, and client projects as they become available.

---

## Phase 4: Production Gate & Launch

- [ ] **Feature Selection Review**: Revisit the chisel menu in `hugo-launch.toml` (e.g. enable `gallery`, `projects`, or `reviews` once real assets exist).
- [ ] **Evidence & Approval Signing**: Populate `data/evidence.json` with SHA-256 hashes and reviewer sign-offs for all production sources.
- [ ] **Production Domain & Cloudflare Pages**:
  - Configure production domain and Cloudflare Pages project.
  - If online intake is desired, enable Cloudflare Turnstile, D1 database, and Pages Functions.
- [ ] **Final Pre-Flight Release Check**: Run `scripts/release_check.py` against the production domain to verify sitemaps, canonical tags, CSP headers, and link integrity.
