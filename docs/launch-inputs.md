# Owner inputs before launch

**Current instruction: leave contacts blank for the review preview.** No phone or email is configured; the site says so rather than showing a placeholder. The evidence register is empty.

## First decision

Confirm the business phone or email that should be public. Then confirm the business identity and the actual service coverage; the current copy has no town list at all.

## Minimal launch checklist

- [ ] Real contact details and production HTTPS domain in the selected profile/launch overlay.
- [ ] Confirm `coverageConfirmed`, town/state/county records, public-address permission, normal SMS capability, separate emergency SMS capability, hours and `contactResponse`.
- [ ] Guides have real publication/review dates, named authors and reviewers.
- [ ] Confirmed business name, service descriptions, coverage wording, and contact preferences.
- [ ] Approved hero image, with permission to publish it.
- [ ] Review of the homepage, core FAQs, process descriptions, service pages, and contact/estimate copy.
- [ ] Review of privacy, terms, and accessibility wording.
- [ ] Choice of optional modules. Start from `hugo-launch.toml`; inactive datasets and pages need no business approval while unpublished; shared rendering code still participates in technical review.
- [ ] Phone, SMS, and email handoffs checked on the intended devices.
- [ ] Production gate passes, followed by explicit deployment authorization and live checks.

## Optional evidence

| Module | Required human evidence |
| --- | --- |
| Projects/gallery | Actual jobs, accurate scope/outcomes, photo ownership and permission; illustrative data must be replaced |
| Reviews | Exact quote, attribution, specific source, and evidenced publication date |
| About/team | Approved business history, names, roles, biographies, and photos |
| Stats/credentials | Real quantities, founding year, license/insurance facts and approved wording |
| Pricing/financing/warranty | Actual offers, terms, exclusions, accepted payment methods, and review ownership |
| Careers/promo/emergency | Current openings, real availability, confirmed emergency capability/contact, review date |
| Field guides | Technical review, accurate scope/jurisdiction, appropriate sources, approved images |

## Record approval of the exact revision

Generate the required-file inventory for the selected launch configuration:

```sh
.venv/bin/python scripts/review_packet.py --output /tmp/jeff-owner-review.md
```

Review the file and its evidence. Only after approval, update its record in `data/evidence.json`: `approved`, `sha256`, `reviewer`, `reviewedOn`, `sources`, and optional `reviewAfter`. The inventory supplies hashes, not approval. Use real source references and actual dates. Keep private source evidence outside the public site repository; the record can refer to an internal evidence ID.

For credentials, pricing, and other datasets with `verified`, set the correctly typed field only when its content is confirmed. Replace placeholder media and clear `placeholder` only after review. Hash the final file after those edits. A changed hash requires another review.

Do not mark example content approved to obtain a green result. Tests use isolated synthetic fixtures; those approvals never apply to this repository's business data.
