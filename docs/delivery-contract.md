# Optional online delivery: acceptance contract

**Local adapter implemented; activation and live acceptance pending.** The optional
Cloudflare adapter is controlled by `params.intake.enabled` (default false).
The legacy `formEndpoint` setting remains unsupported and empty. The adapter has
one fixed same-origin route, `/api/project-request`; it does not accept arbitrary
POST destinations. See [site operations](site-operations.md) for configuration,
recovery, external acceptance, and retained production gates.


The unsafe generic POST behavior remains removed. `formEndpoint` must remain empty; production rejects a nonempty value.

Current supported handoffs are local copy/download and user-completed email/text/call. Copying or opening an app is not evidence that the contractor received an inquiry.

Before activation, confirm the destination, data handling, and response expectations. The adapter must continue to satisfy:

1. Explicit HTTPS endpoint and request schema; no client-side credentials.
2. Validation of all required fields immediately before sending, including edits after draft preparation.
3. A usable reply channel compatible with the visitor's choice.
4. A stable submission ID and durable D1 receipt idempotency. Notification delivery to the operator email inbox is attempted as a separate best-effort operation.
5. Explicit response validation. HTTP 2xx alone is not a delivery receipt.
6. States for prepared, sending, accepted, rejected, and delivery unknown.
7. Timeout-after-acceptance and connection-loss handling that does not falsely say nothing was sent.
8. A recovery path that preserves the submitted revision and avoids duplicate retries.
9. Destination-specific privacy wording, retention policy, and accessible feedback.
10. A real end-to-end acceptance check in the selected provider's test environment, followed by owner-controlled activation.

Required cases: malformed contact, required field cleared after preview, rejection, malformed success, duplicate click, timeout before acceptance, timeout after acceptance, retry, and receipt for the wrong submission ID.

A neutral `/thank-you/` page is retained for old links. It never claims delivery merely because it was opened.

Optional device drafts are independent of delivery. Saving is opt-in, scoped by profile and site path, and expires after seven days when next accessed. Restore is explicit; storage failure must leave the form usable and say that changes were not saved. See the rendered privacy page for the visitor-facing explanation.
