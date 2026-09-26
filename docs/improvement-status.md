# Current implementation and next actions

Updated September 25, 2026. This repository is the **Jeff Does Doors client
site** — a single Hugo site for one barn-door contractor. It was adapted from a
reusable construction master that lives in its own repository; the sculpting CLI,
the second demonstration profile, and the module-guide page were removed here
because a client copy has no use for them and they had already broken.

An optional Cloudflare Pages Functions, Turnstile, and D1 intake adapter is
implemented and disabled by default.

**Status: verified locally via `scripts/verify-local.sh` (19 Python tests, 36
Node tests, feature-menu check, and the staging release gate all passing).
Business approvals and live Cloudflare deployment are pending.**

| Area | State | Remaining acceptance/input |
| --- | --- | --- |
| Identity | Barn-door catalog, specialty, copy, brand mark and hero are Jeff's; engine fallbacks no longer name another business | Jeff's review of every proposed service and answer |
| Module selection | 6 of 23 features selected: mobile contact bar, about, service area, FAQ, contact, legal | Enable more only as evidence and copy are approved |
| Approval gate | Discovers all layouts, assets, static JS, selected config, active content and referenced media in both Python and Hugo | 109 required sources, all unapproved; `data/evidence.json` is empty |
| Release receipt | Refuses to release without a nameable Git revision; records `null` rather than a placeholder when Git cannot answer | Repository has no commits yet |
| Inquiry funnel | No silently selected service, contextual questions, clear local handoffs, nothing sent | Jeff's contact details; real device recipient/body checks |
| Online intake | Adapter implemented, disabled; runtime service IDs match the rendered catalog | Provider decision, environment setup, end-to-end acceptance |
| Recovery | Opt-in browser draft, explicit restore/delete, seven-day expiry | Browser, expiry and denied-storage checks on real devices |
| Assets | 9 WebP images (hero, 4 services, 3 gallery doors, workshop, dark timber CSS texture) generated and documented; master PNGs kept in `.attic/` | Authentic photography of actual work from Jeff |
| Gallery data | `data/gallery.yaml` updated with 8 barn-door records, category tags, and AI concept disclosure alt-texts | Client photo collection when ready to enable feature |
| Deselected modules | Remaining optional pages are `draft: true` and datasets remain for future enablement | Full rewrite before any further module is selected |

## Next action

Stage and commit this source across logical bundles. The repository has no Git history, so there is no recovery point and no revision a release receipt can name until initial commits are made.


Then run:

```sh
bash scripts/verify-local.sh
```

This is local verification, not approval or deployment. Then perform the manual
cases in [verification](verification.md).

## Business-dependent work

The first question is whether Jeff builds doors, installs supplied doors, or
both. That answer gates the service copy and two FAQ answers, so it is worth
resolving before any other content review.

Then: real contact details, domain, confirmed service territory, opening and
response expectations, offered services and exclusions, authentic job media and
rights. Optional credential, pricing, financing, emergency and warranty claims
require actual business terms. Record approval of exact revisions. The code
intentionally does not invent these inputs.

## Later enhancements with a concrete decision first

- Online submission/CRM: choose provider and receiving workflow; implement and
  accept the delivery contract.
- Analytics/call attribution: choose metrics and privacy treatment; distinguish
  intent from receipt and booked work.
- Client content management: choose whether file-based editing remains
  sufficient before adding a CMS.
- Automated deployment: choose host/domain and separately authorize deployment
  setup; this repository contains no deployment workflow.

These are product decisions, not silently connected capabilities. See
[content strategy](content-strategy.md) for the page and editorial plan.
