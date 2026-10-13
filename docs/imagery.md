# Imagery provenance & assets

All imagery assets on this draft site are illustrative concepts created to flesh out the design layout. They are not Jeff’s work, customer properties, product specifications, or installation diagrams. All master images are archived in `.attic/` and encoded to WebP in `static/images/` via `cwebp`.

## Next-generation concept spread — October 13, 2026

Four new images were created with the built-in image generation tool for the homepage section `#next-openings`, immediately after the conventional door styles. The concepts explore surface, light, folding, and pivoting; they do not establish fabrication, hardware compatibility, safety, product availability, or Jeff’s installation capabilities. The spread and every caption identify the images as AI-generated concepts. Native image links work without JavaScript and do not use the existing gallery lightbox.

Copy and image paths live in `data/next_openings.json`, included in the publication source inventory. The new partial uses explicit `srcset` variants at 480, 960, and 1536 pixels. All compositions remain uncropped at 3:2; dimensions reserve image space and loading is lazy. The twelve encoded files total 1,132,644 bytes; each visitor downloads the size chosen by their browser.

| Full image in `static/images/` | Dimensions | Bytes | Source master in `.attic/next-openings/` |
|---|---|---|---|
| `next-sculpted-oak.webp` | 1536×1024 | 198,686 | `sculpted-oak.png` |
| `next-amber-glass.webp` | 1536×1024 | 173,738 | `amber-glass.png` |
| `next-folding-screen.webp` | 1536×1024 | 208,478 | `folding-screen.png` |
| `next-terrazzo-pivot.webp` | 1536×1024 | 164,206 | `terrazzo-pivot.png` |

Each full image has matching `-480.webp` (480×320) and `-960.webp` (960×640) variants, encoded with `cwebp -q 80 -resize WIDTH 0`.

Prompt direction: photorealistic architectural concept visualizations, 3:2 landscape, warm cream plaster, earthy mid-century rooms, natural daylight, full door visible, no people, text, logos, or watermarks. Subjects: flowing wave relief in an oak sliding slab with bronze track; amber reeded-glass panels in rounded bronze frames; four hinged slatted walnut panels gathered into a zigzag; and a coral terrazzo-faced panel turning on an offset pivot. These are visual studies, not installation diagrams.

The local Hugo preview was visually reviewed at desktop, 390px, and 320px viewport widths; a full-size image destination also opened successfully. `git diff --check` passed. Four owner-run regressions in `tests/test_next_openings.py` cover section placement with the gallery disabled, accessible labels and disclosures, responsive image/subpath destinations, and publication inventory coverage. They were authored but not executed; run `bash scripts/verify-local.sh` for the complete local gates. Browser observations do not establish device or assistive-technology acceptance.

## Image inventory

| Asset | Dimensions | Size | Purpose / Placement | Source master in `.attic/` |
|---|---|---|---|---|
| `images/barn-door-illustration.webp` | 1536×1024 | 123 KB | Homepage editorial room image; profile hero fallback | `barn-door-illustration.png` |
| `images/barn-door-pantry.webp` | 1200×896 | 44 KB | Service 01 (`barn-door-installation`), Gallery | `barn-door-pantry.jpg` |
| `images/barn-door-walnut.webp` | 1200×896 | 80 KB | Active specialty homepage hero, Service 02 (`barn-door-replacement`), Gallery and components | `barn-door-walnut.jpg` |
| `images/barn-door-french-glass.webp` | 1200×896 | 91 KB | Gallery (double French sliding doors) | `barn-door-french-glass.jpg` |
| `images/barn-door-oak-slab.webp` | 1200×896 | 37 KB | Gallery (minimalist rift-cut oak slab) | `barn-door-oak-slab.jpg` |
| `images/barn-door-hardware.webp` | 1200×896 | 79 KB | Service 03 (`tracks-hardware`), Gallery | `barn-door-hardware.jpg` |
| `images/barn-door-craftsman.webp` | 1200×896 | 79 KB | Gallery (amber Craftsman horizontal panel) | `barn-door-craftsman.jpg` |
| `images/barn-door-floor-guide.webp` | 1200×896 | 97 KB | Service 04 (`barn-door-adjustments`), Gallery | `barn-door-floor-guide.jpg` |
| `images/barn-door-workshop.webp` | 1200×896 | 155 KB | About page (`/about`), Gallery | `barn-door-workshop.jpg` |
| `images/barn-door-bypass.webp` | 1200×896 | 85 KB | Gallery (double bypass closet sliders) | `barn-door-bypass.jpg` |
| `images/barn-door-chevron.webp` | 1200×896 | 92 KB | Gallery (chevron pattern feature door) | `barn-door-chevron.jpg` |
| `images/barn-door-frosted-glass.webp` | 1200×896 | 41 KB | Gallery (frosted reeded glass privacy slider) | `barn-door-frosted-glass.jpg` |
| `images/barn-door-mirrored.webp` | 1200×896 | 63 KB | Gallery (full-length mirror dressing slider) | `barn-door-mirrored.jpg` |
| `images/wood-texture-dark.webp` | 1376×768 | 274 KB | Homepage closing section material study (`.contact__material`) | `wood-texture-dark.jpg` |

## Current component use

The active door specialty selects `barn-door-walnut.webp` in `data/specialties.yaml`; the homepage and social-image fallback resolve that selection. The Gallery finish selector and project-story component reuse existing illustrations. Finish choices show different design concepts, not exact recolors or purchasable product configurations. The About roster uses decorative text initials rather than implied staff photographs. No additional raster assets were created for the component, mobile, copy or Easter-egg passes.

## Original hero illustration and retained provenance

- Asset: `static/images/barn-door-illustration.webp` (1536×1024, 123 KB).
- The 2.2 MB PNG it was encoded from is kept out of the build in `.attic/`, which is git-ignored.
- Created with the built-in image generation tool on September 25, 2026.
- AI-generated illustration; not Jeff’s work, a product specification, an installation diagram, or a customer property.
- Identified in the review notice. Replace with approved actual work when available.

### Original hero prompt

Use case: photorealistic-natural. Asset type: wide website hero photograph for Jeff Does Doors, a contractor specializing in barn-style doors; illustrative concept only, not a real customer project. Subject: one beautifully made natural oak sliding barn-style interior door with simple vertical planks and subtle horizontal rails, matte black steel overhead track, visible black rollers and a simple black pull handle. Door installed on the right side of a wide interior opening, partially open to a warmly lit quiet home room beyond. Believable complete track with room for the door to slide sideways, accurate plumb architectural details, premium craftsmanship with warm wood grain. Modest welcoming residential interior, warm plaster walls and wood floor, soft daylight. Composition: wide landscape 3:2 editorial architectural photograph, straight vertical lines; door and opening in the right half, left half has quiet darker shaded plaster wall with ample low-detail space for website text overlay. No people, no exterior entry doors, no farm or actual agricultural barn, no signage, no text, no logos, no watermark, no before/after. Warm, understated, practical, not a luxury mansion.

