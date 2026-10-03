#!/usr/bin/env python3
"""Bounded operator commands. Reads D1; previews status changes unless --execute is set."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import urllib.request
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
UUID = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.I)

def query_for(action, receipt=None, status=None):
    if action != 'list' and not UUID.fullmatch(receipt or ''):
        raise ValueError('Use the exact UUID receipt from the saved inquiry.')
    if action == 'list':
        return "SELECT id, created_at, lead_status, notification_status, notification_attempts FROM project_requests WHERE purged_at IS NULL ORDER BY created_at DESC LIMIT 50;"
    if action == 'show':
        return f"SELECT id, payload_json, lead_status, notification_status, notification_error FROM project_requests WHERE id='{receipt}' AND purged_at IS NULL;"
    if action == 'status' and status in ('new', 'contacted', 'closed'):
        contacted = "COALESCE(contacted_at, CURRENT_TIMESTAMP)" if status == 'contacted' else 'contacted_at'
        closed = 'CURRENT_TIMESTAMP' if status == 'closed' else 'NULL'
        return (f"UPDATE project_requests SET lead_status='{status}', contacted_at={contacted}, closed_at={closed}, updated_at=CURRENT_TIMESTAMP "
                f"WHERE id='{receipt}' AND purged_at IS NULL RETURNING id, lead_status, contacted_at, closed_at;")
    raise ValueError('Unsupported operator action or status.')

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Notification endpoint redirected. Check the configured origin; no redirect was followed.')

def retry_notification(origin, token, receipt):
    parsed = urlsplit(origin)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path not in ('','/'):
        raise ValueError('OPERATOR_ORIGIN must be the confirmed HTTPS site origin, without a path, query or credentials.')
    if not UUID.fullmatch(receipt or '') or len(token) < 32:
        raise ValueError('A receipt UUID and configured OPERATOR_TOKEN of at least 32 characters are required.')
    request = urllib.request.Request(origin.rstrip('/') + '/api/notifications',
        data=json.dumps({'id':receipt}).encode(), headers={'Content-Type':'application/json', 'Authorization':'Bearer ' + token}, method='POST')
    with urllib.request.build_opener(NoRedirect).open(request, timeout=20) as response:
        return json.loads(response.read(65536))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['list','show','status','retry-notification'])
    parser.add_argument('receipt', nargs='?')
    parser.add_argument('--status', choices=['new','contacted','closed'])
    parser.add_argument('--database', help='Exact D1 database name or binding')
    parser.add_argument('--config', help='Explicit Wrangler config; required for remote D1')
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument('--local', action='store_true')
    target.add_argument('--remote', action='store_true')
    parser.add_argument('--execute', action='store_true', help='Apply the displayed mutation or notification retry')
    args = parser.parse_args()
    try:
        if args.action == 'retry-notification':
            if not args.remote: raise ValueError('Notification retries use --remote and the explicitly configured OPERATOR_ORIGIN.')
            if not UUID.fullmatch(args.receipt or ''): raise ValueError('Use a receipt UUID.')
            if not args.execute:
                print(f'Preview: retry notification for {args.receipt}; use --execute after confirming OPERATOR_ORIGIN and OPERATOR_TOKEN in your environment.')
            else:
                print(json.dumps(retry_notification(os.environ.get('OPERATOR_ORIGIN',''), os.environ.get('OPERATOR_TOKEN',''), args.receipt), indent=2))
            return 0
        if not args.database or not re.fullmatch(r'[A-Za-z0-9_-]+', args.database): raise ValueError('Supply the exact D1 --database name or binding.')
        if args.remote and not args.config: raise ValueError('Remote D1 requires an explicit --config; inspect its account and database first.')
        config = Path(args.config or ROOT / 'wrangler.local.jsonc').resolve()
        if not config.is_file(): raise ValueError('Wrangler config does not exist.')
        query = query_for(args.action, args.receipt, args.status)
        if args.action == 'status' and not args.execute:
            print(f'Preview only — {"remote" if args.remote else "local"} database {args.database}, config {config}\n{query}')
            return 0
        runner = shutil.which('wrangler')
        if not runner: raise ValueError('Wrangler is not on PATH. Install/configure your chosen Cloudflare CLI before operating D1.')
        # No shell interpolation; values in SQL are constrained UUIDs/enumerations.
        result = subprocess.run([runner,'d1','execute',args.database,'--config',str(config),
            '--remote' if args.remote else '--local','--json','--command',query], cwd=ROOT, check=False)
        return result.returncode
    except Exception as error:
        # Never print tokens, response bodies or request headers on errors.
        print(f'Operator command stopped: {error}', file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
