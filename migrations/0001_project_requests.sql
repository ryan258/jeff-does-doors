CREATE TABLE project_requests (
  id TEXT PRIMARY KEY,
  payload_hash TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  consent_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  lead_status TEXT NOT NULL DEFAULT 'new' CHECK (lead_status IN ('new', 'contacted', 'closed')),
  contacted_at TEXT,
  closed_at TEXT,
  purged_at TEXT,
  notification_status TEXT NOT NULL DEFAULT 'pending'
    CHECK (notification_status IN ('pending', 'sending', 'accepted', 'failed')),
  notification_attempts INTEGER NOT NULL DEFAULT 0,
  notification_error TEXT,
  notification_claim TEXT,
  notification_lease_until INTEGER,
  notification_accepted_at TEXT,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CHECK ((lead_status = 'closed') = (closed_at IS NOT NULL))
);
CREATE INDEX project_requests_delivery ON project_requests(notification_status, notification_lease_until);
CREATE INDEX project_requests_lifecycle ON project_requests(lead_status, closed_at);
