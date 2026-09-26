# Google Business Profile: owner-led setup and maintenance

Status: an operating proposal. This repository does not establish profile ownership, current listing contents, or review authenticity. No Maps or review URL is configured for Jeff, and no review excerpt is approved.

## Confirm identity first

Ask Jeff whether he already manages the existing profile. Confirm that the profile belongs to this business before editing or creating anything. Resolve the business base and actual service coverage; neither a map pin nor draft website copy establishes those facts.

Use the [Google Business Profile help center](https://support.google.com/business/) for the current interface and eligibility rules. Do not infer a registered name, qualifications, service area, or current availability from another business with a similar name.

## Ownership

Keep primary ownership with the business. A manager invitation to Ryan is a separate owner-controlled access decision.

Google's current ownership guidance gives an existing owner three days to respond to an ownership request. It directs service-area businesses without a physical shop or office to contact support for a transfer request. A claim option after nonresponse is not guaranteed. Follow the route appropriate to this business. [Google ownership guidance](https://support.google.com/business/answer/4566671?hl=en-uk)

## Align the website and profile

| Information | Repository source | Action |
| --- | --- | --- |
| Business identity and contact | `profiles/<client>.toml`, launch overlay | Enter the owner's actual approved values; remove review placeholders |
| Coverage | `params.serviceArea`, `data/service_area.yaml` | Confirm the places actually served and use consistent wording |
| Services | `data/services.yaml`, service pages | List only work actually offered |
| Public website | `params.productionURL` | Add the final live HTTPS URL after deployment verification |
| Review profile | `params.reviewURL` | Destination for reading reviews |
| Review request | `params.reviewRequestURL` | Separate optional owner-confirmed review-writing link |
| Images and project outcomes | `data/evidence.json` and media sources | Use approved material with permission |
| Hours and urgent availability | Owner records | Verify directly; do not infer a 24-hour service from an emergency page |

Choose the available business categories that accurately describe the work. Confirm current category names in the profile interface; this document does not promise a ranking effect. Use current Google guidance for address visibility and service-area settings.

## Reviews

Ask customers for honest feedback without incentives or selective positive-review filtering. Verify the exact quote, attribution, date, and source before quoting it on the site. Author-profile URLs may help locate a review but are not evidence of its exact text or publication date.

Keep profile-view and review-request URLs separate. The website's “read reviews” action should show customer evidence; its optional “leave a review” action should start the writing flow. Do not replace both with one write-review URL.

Responding to or soliciting reviews is an external communication and requires explicit owner instruction. No response, invitation, or profile change is authorized by this document.

## Posts and other profile features

Google's current post documentation describes archiving posts older than six months unless a date range is set. Do not use the old seven-day visibility claim as a scheduling rule. Confirm the current interface and any feature-specific requirements when acting. [Google post guidance](https://support.google.com/business/answer/7342169?hl=en-GB)

Use available profile features only when they reflect a real, approved business offer. Avoid publishing placeholder prices, fictional project outcomes, unsupported credentials, or assumed appointment availability.

## Sustainable maintenance

Choose a cadence Jeff can maintain. Review contact details, service coverage, offers, hours, and new photos when they change. Revisit this guide's external instructions before using them; source check for the ownership/post sections: September 14, 2026.

Success should be measured through the business's actual useful inquiries and completed work. Analytics, call tracking, and CRM attribution are optional future decisions with their own implementation and privacy requirements; none is connected by this guide.
