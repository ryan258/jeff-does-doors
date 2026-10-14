# Architecture and publication contract

## Flow

Engine defaults + selected business profile + environment/module overlay, Markdown, YAML and JSON data → Hugo templates → static HTML, CSS, JavaScript, search JSON, sitemap, and RSS → the visitor's browser.

The browser prepares a brief locally by default. Email, text, call, copy, and download are explicit handoffs. An optional Cloudflare Pages Functions, Turnstile, and D1 intake adapter is implemented for online sending, but is disabled by default.

## Shared policy

`data/publishing.json` defines features, source files, section ownership, and dependencies. Both the Hugo feature helper and Python validation consume it. Unknown flags and malformed boolean settings are validation errors. A missing or non-boolean flag is never treated as enabled by templates.

`page-disabled.html` applies the registry to page front matter and section descendants. The base layout, search, sitemap, RSS, links, and structured data use that decision. Disabled routes deliberately return neutral noindex HTML rather than their original content. They are retained URLs, not HTTP 404 responses.

Pages explicitly marked as drafts are omitted from normal builds. The component guide uses `reviewOnly: true` and its own `noindex` setting: the full catalogue renders in review mode, is excluded from search/sitemap, and becomes the neutral unavailable page outside review mode. It does not introduce another feature flag.

## Content evidence

`data/evidence.json` contains an approval record per reviewed source or image. A valid record requires actual boolean `approved: true`, a matching SHA-256 digest, reviewer, source references, and an actual review date. An optional re-review date can make an approval overdue. Dates, names, and outcomes cannot be inferred from placeholder copy.

The digest covers exact file bytes. Editing approved content invalidates the approval. Configuration is included because changing a business claim changes what is published. A separate launch overlay selects modules and replaces preview contact placeholders; the checker validates the effective values.

Python uses PyYAML's safe loader with duplicate-key rejection and `tomllib`/`tomli`. Dataset schemas validate the actual rendered record structures. Pricing, financing, warranties, jobs, people, reviews, and imagery participate in the policy. The evidence record approves complete copy, not only an image flag.

Required sources include all rendering templates, asset sources and static JavaScript, active registered datasets, shared brief/survey/guidance schemas, release/operator scripts, workflow definitions, Python requirements, selected configuration files, the profile manifest, active Markdown pages discovered from disk, and referenced images. This closes the former shared-template inventory gap. Review-only pages are excluded from production content. A newly added page cannot bypass evidence collection by being omitted from the registry.

Direct indexable production Hugo builds are blocked. The release command first validates the explicit configuration-file list, dates, schemas, contacts, and source approvals, then invokes Hugo with an internal workflow marker and audits the generated artifact. Ambient Hugo environment overrides and implicit configuration directories are excluded. Hugo retains its missing/incomplete/changed source checks during that invocation; the marker is not a credential or owner approval. Acceptance evidence remains revision-bound even when the intake UI is disabled, and optional Cloudflare redirects participate in source review.

## Separation of responsibilities

- `content_policy.py`: parsing, source schemas, feature resolution, evidence.
- `release_check.py`: CLI, build, HTML/JSON/XML checks, artifact/report creation.
- `feature_docs.py`: deterministic feature documentation.
- `review_packet.py`: read-only evidence inventory for human review.
- `draft-storage.js`: whitelisted, expiring device drafts with explicit opt-in in the UI; no network delivery.
- `brief-core.js`: pure search validation/ranking helpers.
- `site.js`: independent feature initialization over a small shared lookup scope; failures are isolated per feature and covered by an empty-document smoke test; no arbitrary POST integration.
- `contractor-choices.js`: independently enhances native radio/panel groups; validates mappings before hiding fallback content, preserves restored choices and has no network or storage behavior.
- `style-guide.js`: catalogue-only search, family filters, fragment recovery and copy/failure feedback.
- SCSS partials: `_modern.scss` owns the mobile header/hero layout; `_survey.scss` owns survey styles. `_contractor.scss`, `_style-guide.scss`, `_easter-eggs.scss`, and `_next-openings.scss` are imported after those shared layers.

## Component library and visitor composition

The [living style guide](component-library.md) renders 42 specimens from real partials: 32 contractor components, six shared patterns and four foundations. `data/component_library.json` provides review fixtures and contracts. Production page copy lives separately in `data/site_components.json`; 24 components have placements across 12 routes. The eight enquiry-through-aftercare additions currently render only in the guide; their reusable partials are allowed by the wrapper without new JavaScript or visitor-page copy. The six project-paperwork patterns serve the four service pages, Contact, and FAQ through the same wrapper without adding scripts. Contact keeps the brief form before access planning; FAQ links to the existing survey and leaves unavailable project documents as plain text.

`site-component.html` validates an explicit component allowlist, checks optional feature dependencies, supplies section headings and prefixes IDs from each placement key. Missing records and unknown component names fail the build. Templates choose the placements; the dataset's `page` field supplies catalogue links. About's crew/notes obey `team`, and its credential list obeys `credentials`. The existing base layout suppresses disabled pages before their content renders.

Only Home and Gallery request the shared choice script through the page store. The guide deduplicates its own specimen script declarations. Without JavaScript, choice controls stay hidden and all panels remain readable; native checkboxes and disclosures still work. The guide links to existing brief/survey workflows instead of cloning their forms.

`easter-egg.html` is a Jeff-profile-only native disclosure, used in three places outside task controls. Home/About crew notes obey `team`; Gallery obeys its page flag. It escapes all supplied text and adds no storage, script or automatic announcement. The notes are documented in the guide's library map, not counted as additional specimens.

The visitor component dataset is an explicit publication core source; rendering assets and templates are already inventoried automatically. Fictional reviews, crew, project stories and planning examples do not establish real business facts. Existing dataset display flags such as `verified` or `approved` are not substitutes for the empty revision-bound evidence register.

`data/next_openings.json`, `layouts/partials/next-openings.html`, and `_next-openings.scss` compose the homepage concept spread between styles and catalog. The partial renders four uncropped 3:2 responsive WebP studies (480w, 960w, 1536w) with visible AI disclosures and native full-image links, independent of the gallery lightbox or JavaScript. The dataset is registered in `data/publishing.json`.

## Assets and environments

Source images are mounted into Hugo's asset pipeline to generate responsive variants. Browser JavaScript and CSS use content-fingerprinted URLs. Original images remain available for no-JavaScript gallery links and enlarged views.

Staging: selected client features, noindex/nofollow, no sitemap or RSS. These controls do not provide privacy or access control.

Launch: explicit minimal overlay, production URL, approved sources, artifact audit. Deploy the exact audited artifact. A successful build is not proof of remote hosting, customer delivery, accessibility conformance, or business approval.

## Reusable master

`site-profile.json` selects the profile for Python entry points. Hugo CLI commands must explicitly name it. `data/specialties.yaml` controls editorial emphasis and service ordering; `data/services.yaml` supplies offered services, inquiry choices, search vocabulary, related services and schema. Service IDs must stay in step across `data/services.yaml`, `content/services/`, the specialty `serviceOrder`, and the Functions runtime `INTAKE_SERVICES`. The reusable master this site was adapted from lives in its own repository; the sculpting tools are not carried here.

## Inquiry and survey contracts

`assets/contracts/brief-schema.json` is the versioned inquiry wire contract. Hugo mounts `assets/contracts` into its data namespace and renders the exact string choices and browser/server normalization reads the same file. Human-readable choice strings are deliberately retained as wire values to preserve saved drafts; change them as a contract migration, not a copy edit. Service IDs still come from `data/services.yaml`. Starting point and target date participate in the submitted payload hash. The shared delivery-status partial reflects available delivery capability rather than a hardcoded preview claim.

`data/door-guidance.json` supplies the common measurement reference points used in guides and FAQ answers. `faq-answer.html` resolves a delivery-state answer, one of the four supported guidance references, or plain answer text; the source policy validates those alternatives. The manufacturer instructions linked there are examples; the actual selected model and revision belong in each job packet.

`assets/contracts/survey-schema.json` supplies the single-opening fields and check states. `survey-core.mjs` validates file boundaries, numeric/fraction values and packet output; `survey.js` manages accessible controls, explicit browser storage and import/export/print. Only the survey route loads that bundle. Canonical JSON contracts live inside assets for both Node and Hugo imports; Hugo data mounts expose the same bytes to templates. Generated editor mappings are disabled to keep builds from modifying approved source. All imported text is assigned through form values or `textContent`; a packet cannot inject HTML or select a network destination. JSON import is size-bounded and versioned. Device saving is optional; the tool is not a multi-job datastore or installation approval engine.

## Release provenance and host boundaries

The release command now refuses dirty production source, treats Hugo warnings as failures, inventories exact source and output hashes, and compares source hashes after building. `release.json` is excluded from its own output hash inventory. Approvals and hashes are ordinary records, not cryptographic signatures. Repository write access can alter the guards; branch protections and independent review are operational controls outside these scripts.

The existing `pages.yml` workflow builds and deploys GitHub Pages staging on push to `main` or dispatch. `validate.yml` validates PRs with read-only repository permissions and no deployment job. Cloudflare production is separately configured and authorized. `_headers` is not a GitHub Pages header mechanism. No local build proves live header behavior.

The asset import and data mount design follows [Hugo JavaScript build documentation](https://gohugo.io/functions/js/build/); editor mapping generation is controlled by the documented [build setting](https://gohugo.io/configuration/build/).
