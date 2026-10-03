# Jeff Does Doors: optional Cloudflare operations

Status: implemented locally on 2026-09-19; **disabled by default and not deployed**.
The Jeff profile has blank contacts, unapproved business
content, and no confirmed production URL. This work does not establish a live
service, email identity, or owner approval. The September master-refactor suite
still needs the owner-run full check below.

## Architecture and visitor behavior

Hugo 0.166.0 Extended continues to produce the site. Local brief preparation,
copy/download, direct handoffs, profile selection, and opt-in seven-day device
drafts remain available. Online sending is a separate action after preparation.
The legacy `formEndpoint` must remain empty; arbitrary POST targets are unsupported.

The adapter uses `/api/project-request` on the same origin, Pages Functions, a
D1 binding named `DB`, and server-validated Turnstile. The endpoint path stays at
the origin root even when static pages use a subpath. A GitHub Pages mirror must
leave `params.intake.enabled = false`; it has no Functions runtime.

Both browser and server validate the current entries against
`assets/js/intake-core.mjs`. The online request requires location, details, a usable
reply channel, compatible reply preference, and explicit sending consent. Service
IDs come from the catalog, not arbitrary titles. All current brief fields are
preserved in a normalized JSON record; no attachments are accepted. The complete
schema includes the business profile, environment, and notice version. Server
configuration must match the generated site.

A UUID and SHA-256 fingerprint identify one exact normalized request. A successful
receipt includes both and is accepted by the browser only when they match.
Identical retries return the saved receipt; changed content with the same UUID
conflicts. The submitted version stays visible separately from the editable draft.
A timeout is uncertain, not proof of failure. Retry the submitted version or
explicitly start a new inquiry after acknowledging possible duplication.

Only UUID, fingerprint, and receipt state go into sessionStorage automatically.
Draft text is saved only through the existing device-saving consent. If a page is
reloaded after an uncertain send, restore the opted-in draft or re-enter the same
entries to retry the same UUID. With no saved draft, the site cannot reconstruct
lost text. Closing the tab or clearing browser storage loses the retry identity;
keep a copy and receipt before doing so. Online sending stops before network I/O
if it cannot save its identity. Copy/download/direct contact remain available.
If metadata disappears while an earlier submitted version is still in memory,
Send and Retry require an explicit new-request confirmation before another send.
The new attempt displays its own submitted version beside its receipt.

## Configure an isolated preview first

No real domain, account, sender, recipient, retention policy, preview database,
production database, registrar/DNS owner, or known-good deployment ID is recorded
yet. Confirm these before external activation. Do not reuse a production database,
recipient, or Turnstile widget in preview.

Add a site-specific Hugo overlay after the selected profile and staging config:

```toml
[params.intake]
enabled = true
environment = "preview"
siteKey = "REPLACE_WITH_PREVIEW_WIDGET_SITEKEY"
consentVersion = "REPLACE_WITH_APPROVED_NOTICE_VERSION"
retentionNotice = "REPLACE_WITH_APPROVED_RETENTION_AND_CONTACT_NOTICE"
```

Public configuration contains no secrets. For production, use environment
`production`, the actual HTTPS base URL, and matching completed acceptance evidence.
Configure the same values in the **Functions runtime**, not only the build shell:

| Runtime binding/value | Required meaning |
| --- | --- |
| `DB` | Environment-specific D1 database; apply `migrations/0001_project_requests.sql` once |
| `INTAKE_ENABLED` | Exact string `true`; missing/false rejects new intake |
| `INTAKE_ENV` | `preview`, `production`, or loopback-only `local` |
| `INTAKE_PROFILE` | Selected `params.profileID` |
| `INTAKE_SUPPORTS_SMS` | Exact `true` or `false`, matching the profile |
| `INTAKE_SERVICES` | JSON array of all service IDs rendered in the form |
| `TURNSTILE_HOSTNAMES` | Comma-separated exact allowed request/token hostnames; no wildcards |
| `CONSENT_VERSION` | Matches the generated notice version |
| `TURNSTILE_SECRET_KEY` | Secret for this environment's widget; verified server-side |
| `CF_ACCOUNT_ID` | Account containing the configured email service |
| `EMAIL_API_TOKEN` | Secret with the required email-sending permission |
| `NOTIFICATION_FROM` | Fixed verified custom-domain sender |
| `NOTIFICATION_TO` | Fixed verified operator inbox; a test inbox in preview |
| `OPERATOR_TOKEN` | Independent random secret, at least 32 characters, for recovery |

Current catalog IDs: `barn-door-installation`, `barn-door-replacement`,
`tracks-hardware`, `barn-door-adjustments`. These must match `data/services.yaml`
exactly; a stale list rejects every inquiry. Unspecified and multiple
service projects are supported separately. Jeff currently has SMS disabled.

`wrangler.local.jsonc` is deliberately local-only, contains a placeholder database
UUID, and starts with intake disabled. For a local exercise, set `INTAKE_ENABLED`
to `true`, use a Hugo local overlay with a loopback base URL and the documented
Turnstile dummy sitekey, and put the dummy secret in an ignored `.dev.vars` file.
Use explicit `--local` for migrations. Never point this fixture at a remote DB:

```sh
npx wrangler@3 d1 migrations apply DB --local --config wrangler.local.jsonc
npx wrangler@3 pages dev public --config wrangler.local.jsonc
```

Build the matching local artifact first. Local mode never sends real notification
email. Deployed previews require real widget keys; dummy keys are rejected outside
loopback local mode. Runtime host/action validation and an eight-second verification
timeout apply before storage. Set account-level abuse controls and observe quotas
before allowing public traffic; no strict application rate limiter is claimed.

## Notification and lead recovery

The chosen transport is Cloudflare Email Service REST, addressed only to the fixed
verified operator destination. It uses the saved record, includes name/contact/reply
preference and the receipt ID, and omits property/project notes. An email contact is
used as Reply-To; a phone-only contact is not converted into an email address.
Notifications are marked pending in the same database write as the inquiry.

Delivery is best-effort background work with a 60-second claim lease, ten-second
provider timeout, attempt count, and independent `pending/sending/accepted/failed`
state. Provider acceptance is not proof of inbox delivery or human follow-up.
There is **no scheduler or unattended delivery guarantee**. The operator must check
pending, failed, and expired sending records, including when no email arrived:

```sql
SELECT id, notification_status, notification_attempts, notification_error
FROM project_requests WHERE purged_at IS NULL AND
(notification_status IN ('pending','failed') OR
 (notification_status = 'sending' AND notification_lease_until < unixepoch()*1000));

SELECT id, created_at FROM project_requests
WHERE lead_status = 'new' AND purged_at IS NULL ORDER BY created_at;
```

In an authenticated D1 console, look up a request by its receipt ID to read its
`payload_json`. Do not paste private records into issue trackers or public logs.
For one stalled notification, POST JSON `{"id":"THE_RECEIPT_UUID"}` to
`/api/notifications` with `Authorization: Bearer <OPERATOR_TOKEN>` and
`Content-Type: application/json`. Keep the token in a secret manager; never expose
it to the site/browser bundle. Check the resulting DB state before repeating.
The endpoint exposes no public inquiry listing or content lookup.

Concurrent delivery workers cannot claim the same active lease. A provider may
accept mail immediately before the status write fails; retrying an expired lease
can therefore duplicate a notification. The stable receipt ID makes this apparent.
Mail configuration, quota, or provider failures leave the saved inquiry recoverable.
A database/quota failure cannot produce a confirmed visitor receipt.

Lead status is separate: update `lead_status='contacted'` with `contacted_at` on
actual contact; set `lead_status='closed'` and `closed_at` together on closure.
Retention is still an owner decision. A proposed closed-inquiry period must count
from `closed_at`, never discard unanswered requests based on creation age, and
cover notification copies, exports, backups, and restored data. Preview eligible
IDs/counts before any purge. If clearing `payload_json`, preserve the ID/hash
receipt tombstone for the agreed retry horizon and set `purged_at`; notifications
exclude purged records. Document the separate tombstone deletion horizon.

For recovery, export the **explicitly selected** database to an access-controlled,
ignored `private-exports/` directory using Wrangler D1 export with `--local` or
`--remote` explicitly selected. Import into a separate disposable local database;
compare receipt IDs, hashes, JSON records, and lifecycle/delivery counts before
calling the backup verified. The schema is locally tested; a real Wrangler export,
restore, and off-device recovery exercise remain pending. Never restore over live
intake as a test or email old restored pending rows without reviewing them.

## Acceptance and release

The existing source and generated-artifact release gate remains authoritative.
Revision-bound approval also covers Functions, libraries, migrations, and
routing/headers, optional `static/_redirects`, and `data/intake-acceptance.json`,
including when the static intake UI is disabled because Functions still import it;
the production endpoint itself refuses pending or mismatched acceptance evidence. No approvals were
created by this implementation. Complete that record only after authorized live
preview testing: actual receipt and D1 row, response-loss retry, malformed receipt,
wrong/expired challenge, mail failure/recovery, recipient acceptance, preview/prod
isolation, no-JS fallback, keyboard/narrow-screen use, retention, and restore.
Record real date, exact site/profile/notice, and evidence locations. Local fixtures
are not acceptable replacements for those observations. Re-review changed source
hashes and the actual production configuration before publication.

Before the first verification on a machine, install the pinned Python dependencies
in this repository's virtual environment (the verification script selects it
automatically):

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Run the owner's complete local gate before proceeding:

```sh
cd /path/to/project
bash scripts/verify-local.sh
```

For a production Pages build, use the required release entry point:

```sh
python3 scripts/release_check.py --base-url "$LIVE_SITE_URL" --destination public
```

Direct indexable production Hugo builds fail closed. Hugo templates cannot check
the actual selected configuration-file list, so the release command validates
that list and source approvals before invoking Hugo. It ignores ambient `HUGO_*`
configuration overrides and implicit `config/` directories; put intended settings
in the explicit `--config` files. Its internal `HUGO_RELEASE_GATE` marker is a
workflow interlock, not a credential or owner approval; do not set it manually.

Use `--config` when adding a reviewed intake overlay, include that overlay in
`approvalConfigFiles`, and ensure `productionURL` matches the deployed URL. Publish
only the audited `public` artifact; do not run a second Hugo build after the gate.
The deployed Functions must come from the same approved source revision.

Before cutover, identify the previous working host/deployment, preserve its source
and contact mechanism, inventory DNS/MX/SPF/DKIM/DMARC and registrar DNSSEC/DS,
and document the authorized rollback operator. DNS reversal alone is insufficient
if the previous host receives Cloudflare-only markup. To disable new intake, set
runtime `INTAKE_ENABLED=false` and redeploy an audited static artifact with Hugo
intake disabled; preserve D1 and operator recovery for already accepted requests.
No DNS, provider account, deployment, or external test mail action is authorized
merely by following this runbook.

Inbound custom-domain forwarding and Gmail send-as are separate from application
notifications. Verify the outbound relay, selected Gmail From identity, Reply-To,
and received SPF/DKIM/DMARC results using authorized test recipients before claiming
that correspondence works or that a personal address stays private.

## Provider references checked 2026-09-19

- [Pages D1 bindings](https://developers.cloudflare.com/pages/functions/bindings/#d1-databases).
- [Turnstile server validation](https://developers.cloudflare.com/turnstile/get-started/server-side-validation/): tokens are single-use; retries need fresh verification.
- [Cloudflare Email REST API](https://developers.cloudflare.com/email-service/api/send-emails/rest-api/): provider response is evaluated for the configured recipient.
- [Email pricing](https://developers.cloudflare.com/email-service/platform/pricing/): sending to verified account destinations is free; arbitrary recipients require a paid plan. Account eligibility remains to be verified.
- [D1 Wrangler commands](https://developers.cloudflare.com/d1/wrangler-commands/): local/remote targets and import/export are separate operator choices.

This is a free-tier design under those assumptions, not a permanent zero-cost or
unlimited-capacity promise. Notifications to visitors are intentionally not added.

## Bounded operator helper

`scripts/lead_desk.py` reduces routine SQL entry. It requires an explicit local/remote target, constrains receipt IDs and status values, and previews mutations unless `--execute` is supplied. Listing shows at most 50 receipt/status records without inquiry text; `show` deliberately reveals the selected inquiry. No provider operation was executed during implementation.

With an installed, configured Wrangler CLI and a migrated local fixture:

```sh
python3 scripts/lead_desk.py list --local --database DB
python3 scripts/lead_desk.py show RECEIPT_UUID --local --database DB
python3 scripts/lead_desk.py status RECEIPT_UUID --status contacted --local --database DB
```

Replace the receipt with the real UUID. The status command prints the proposed SQL; add `--execute` to apply it. Remote D1 operations additionally require `--remote --config /path/to/the/reviewed/wrangler-config.jsonc` and the database name or binding. Inspect the selected account/configuration before operating. The helper uses documented [Wrangler D1 command flags](https://developers.cloudflare.com/d1/wrangler-commands/).

Notification recovery uses `retry-notification RECEIPT_UUID --remote`; it previews the action. Execution additionally requires `--execute`, an HTTPS `OPERATOR_ORIGIN` and `OPERATOR_TOKEN` already provided through your private environment. Tokens are not command-line arguments, written to the repository or printed. Redirects are rejected to avoid forwarding credentials to a different endpoint. The tool reports the endpoint result; acceptance by an email API is not proof the recipient read it.

The helper does not replace the retention/export/restore procedures above and does not authenticate a browser inbox. Keep operator access and backups private. Source and output manifests in release receipts identify reviewed bytes; production release also requires a clean Git revision. The October 3 helper and release changes await the owner-run verification command.
