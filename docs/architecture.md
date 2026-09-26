# Architecture and publication contract

## Flow

Engine defaults + selected business profile + environment/module overlay, Markdown, and YAML data → Hugo templates → static HTML, CSS, JavaScript, search JSON, sitemap, and RSS → the visitor's browser.

The browser prepares a brief locally by default. Email, text, call, copy, and download are explicit handoffs. An optional Cloudflare Pages Functions, Turnstile, and D1 intake adapter is implemented for online sending, but is disabled by default.

## Shared policy

`data/publishing.json` defines features, source files, section ownership, and dependencies. Both the Hugo feature helper and Python validation consume it. Unknown flags and malformed boolean settings are validation errors. A missing or non-boolean flag is never treated as enabled by templates.

`page-disabled.html` applies the registry to page front matter and section descendants. The base layout, search, sitemap, RSS, links, and structured data use that decision. Disabled routes deliberately return neutral noindex HTML rather than their original content. They are retained URLs, not HTTP 404 responses.

## Content evidence

`data/evidence.json` contains an approval record per reviewed source or image. A valid record requires actual boolean `approved: true`, a matching SHA-256 digest, reviewer, source references, and an actual review date. An optional re-review date can make an approval overdue. Dates, names, and outcomes cannot be inferred from placeholder copy.

The digest covers exact file bytes. Editing approved content invalidates the approval. Configuration is included because changing a business claim changes what is published. A separate launch overlay selects modules and replaces preview contact placeholders; the checker validates the effective values.

Python uses PyYAML's safe loader with duplicate-key rejection and `tomllib`/`tomli`. Dataset schemas validate the actual rendered record structures. Pricing, financing, warranties, jobs, people, reviews, and imagery participate in the policy. The evidence record approves complete copy, not only an image flag.

Required sources include all rendering templates, asset sources and static JavaScript, active registered datasets, selected configuration files, the profile manifest, active Markdown pages discovered from disk, and referenced images. This closes the former shared-template inventory gap. Review-only pages are excluded from production content. A newly added page cannot bypass evidence collection by being omitted from the registry.

Direct indexable production Hugo builds are blocked. The release command first validates the explicit configuration-file list, dates, schemas, contacts, and source approvals, then invokes Hugo with an internal workflow marker and audits the generated artifact. Ambient Hugo environment overrides and implicit configuration directories are excluded. Hugo retains its missing/incomplete/changed source checks during that invocation; the marker is not a credential or owner approval. Acceptance evidence remains revision-bound even when the intake UI is disabled, and optional Cloudflare redirects participate in source review.

## Separation of responsibilities

- `content_policy.py`: parsing, source schemas, feature resolution, evidence.
- `release_check.py`: CLI, build, HTML/JSON/XML checks, artifact/report creation.
- `feature_docs.py`: deterministic feature documentation.
- `review_packet.py`: read-only evidence inventory for human review.
- `draft-storage.js`: whitelisted, expiring device drafts with explicit opt-in in the UI; no network delivery.
- `brief-core.js`: pure search validation/ranking helpers.
- `site.js`: independent feature initialization over a small shared lookup scope; failures are isolated per feature and covered by an empty-document smoke test; no arbitrary POST integration.
- SCSS partials: original cascade order preserved, with shared state fixes isolated.

## Assets and environments

Source images are mounted into Hugo's asset pipeline to generate responsive variants. Browser JavaScript and CSS use content-fingerprinted URLs. Original images remain available for no-JavaScript gallery links and enlarged views.

Staging: full review menu, noindex/nofollow, no sitemap or RSS. These controls do not provide privacy or access control.

Launch: explicit minimal overlay, production URL, approved sources, artifact audit. Deploy the exact audited artifact. A successful build is not proof of remote hosting, customer delivery, accessibility conformance, or business approval.

## Reusable master

`site-profile.json` selects the profile for Python entry points. Hugo CLI commands must explicitly name it. `data/specialties.yaml` controls editorial emphasis and service ordering; `data/services.yaml` supplies offered services, inquiry choices, search vocabulary, related services and schema. Service IDs must stay in step across `data/services.yaml`, `content/services/`, the specialty `serviceOrder`, and the Functions runtime `INTAKE_SERVICES`. The reusable master this site was adapted from lives in its own repository; the sculpting tools are not carried here.
