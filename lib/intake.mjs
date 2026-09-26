import acceptance from '../data/intake-acceptance.json' with { type: 'json' };
import { normalize, LIMITS } from '../assets/js/intake-core.mjs';
export const HEADERS = {
  'Cache-Control': 'no-store',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
};
export const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
export class IntakeError extends Error {
  constructor(status, message) { super(message); this.status = status; }
}
export function reply(status, body, extra = {}) {
  return new Response(JSON.stringify(body), {
    status, headers: { ...HEADERS, 'Content-Type': 'application/json; charset=utf-8', ...extra },
  });
}
export async function digest(value) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(value)))]
    .map(b => b.toString(16).padStart(2, '0')).join('');
}
export function runtime(env, request) {
  if (env.INTAKE_ENABLED !== 'true' || !['production', 'preview', 'local'].includes(env.INTAKE_ENV) || !env.DB ||
      !env.TURNSTILE_SECRET_KEY || !env.TURNSTILE_HOSTNAMES || !env.CONSENT_VERSION) {
    throw new IntakeError(503, 'The form is temporarily unavailable. Please use the contact address shown beside the form.');
  }
  const hosts = env.TURNSTILE_HOSTNAMES.split(',').map(s => s.trim()).filter(Boolean);
  const url = new URL(request.url);
  if (!hosts.includes(url.hostname)) throw new IntakeError(403, 'This form address is not enabled.');
  if (request.headers.get('Origin') && request.headers.get('Origin') !== url.origin) {
    throw new IntakeError(403, 'Please submit from this site.');
  }
  // Cloudflare's documented dummy keys may only be used on loopback development.
  if (/^[123]x0+AA$/.test(env.TURNSTILE_SECRET_KEY) && env.INTAKE_ENV !== 'local') {
    throw new IntakeError(503, 'Live verification is not configured.');
  }
  if (env.INTAKE_ENV === 'local' && !['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)) {
    throw new IntakeError(503, 'Local configuration cannot serve this address.');
  }
  if (url.protocol !== 'https:' && env.INTAKE_ENV !== 'local') throw new IntakeError(403, 'HTTPS is required.');
  siteConfig(env);
  if (env.INTAKE_ENV === 'production') {
    let origin;
    try { origin = new URL(acceptance.baseURL).origin; } catch { /* pending evidence */ }
    if (acceptance.status !== 'accepted' || origin !== url.origin || acceptance.profile !== env.INTAKE_PROFILE ||
        acceptance.consentVersion !== env.CONSENT_VERSION || !acceptance.testedOn || !acceptance.evidence?.length) {
      throw new IntakeError(503, 'Production intake acceptance is pending. Use direct contact.');
    }
  }
  return hosts;
}
export async function boundedBody(request, limit = 65536) {
  const reader = request.body?.getReader();
  if (!reader) throw new IntakeError(400, 'A form submission is required.');
  const chunks = []; let size = 0;
  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      size += value.byteLength;
      if (size > limit) {
        await reader.cancel();
        throw new IntakeError(413, 'The submission is too large. Please shorten it.');
      }
      chunks.push(value);
    }
  } finally { reader.releaseLock(); }
  const body = new Uint8Array(size); let offset = 0;
  for (const chunk of chunks) { body.set(chunk, offset); offset += chunk.length; }
  return body;
}
export async function verifyToken(data, env, hosts, fetcher = fetch) {
  if (!data['cf-turnstile-response']) throw new IntakeError(403, 'Please complete verification before sending.');
  let result;
  try {
    const response = await fetcher('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST', signal: AbortSignal.timeout(8000),
      body: new URLSearchParams({ secret: env.TURNSTILE_SECRET_KEY, response: data['cf-turnstile-response'] }),
    });
    if (!response.ok) throw new Error('verification_unavailable');
    result = await response.json();
  } catch { throw new IntakeError(503, 'Verification is temporarily unavailable. Your entries are still here; please try again.'); }
  if (!result.success || (env.INTAKE_ENV !== 'local' &&
      (!hosts.includes(result.hostname) || result.action !== 'project-request'))) {
    throw new IntakeError(403, 'Verification expired or failed. Please verify again.');
  }
}

export function siteConfig(env) {
  let services;
  try { services = JSON.parse(env.INTAKE_SERVICES); } catch { /* fail closed below */ }
  if (!/^[a-z0-9-]{1,80}$/.test(env.INTAKE_PROFILE || '') ||
      !['true', 'false'].includes(env.INTAKE_SUPPORTS_SMS) ||
      !Array.isArray(services) || !services.length || services.some(s => typeof s !== 'string' || !/^[a-z0-9-]{1,80}$/.test(s))) {
    throw new IntakeError(503, 'The project form is not configured. Use the direct contact options.');
  }
  return { environment: env.INTAKE_ENV, profile: env.INTAKE_PROFILE, services, supportsSMS: env.INTAKE_SUPPORTS_SMS === 'true', consentVersion: env.CONSENT_VERSION };
}
export async function parseForm(request) {
  const type = request.headers.get('Content-Type') || '';
  if (!/^application\/x-www-form-urlencoded(;|$)/i.test(type)) throw new IntakeError(415, 'Use the project form.');
  const bytes = await boundedBody(request, 262144);
  let text;
  try { text = new TextDecoder('utf-8', { fatal: true }).decode(bytes); }
  catch { throw new IntakeError(400, 'The submission could not be read.'); }
  const fields = new URLSearchParams(text);
  const data = {};
  const limits = { ...LIMITS, 'submission-id': 36, 'cf-turnstile-response': 2048 };
  for (const [key, value] of fields) {
    if (!Object.hasOwn(limits, key) || Object.hasOwn(data, key) || value.length > limits[key]) {
      throw new IntakeError(400, 'Unsupported, repeated, or oversized field.');
    }
    data[key] = value;
  }
  if (!UUID.test(data['submission-id'] || '')) throw new IntakeError(400, 'A valid request ID is required.');
  return data;
}
export function validate(data, env) {
  const input = Object.fromEntries(Object.keys(LIMITS).map(key => [key, data[key] ?? '']));
  try { return normalize(input, siteConfig(env)); }
  catch (error) { throw new IntakeError(400, error.message); }
}
export async function saveInquiry(db, id, payload) {
  const json = JSON.stringify(payload);
  const hash = await digest(json);
  const row = await db.prepare(`INSERT INTO project_requests (id, payload_hash, payload_json)
    VALUES (?, ?, ?) ON CONFLICT(id) DO UPDATE SET id = excluded.id RETURNING id, payload_hash`)
    .bind(id, hash, json).first();
  if (!row?.id) throw new Error('missing_receipt');
  if (row.payload_hash !== hash) throw new IntakeError(409, 'This ID belongs to different details. Resolve the earlier request before starting another.');
  return { id: row.id, hash: row.payload_hash };
}
