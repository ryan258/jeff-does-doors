// Shared browser/server contract. Property order is the canonical hash representation.
export const LIMITS = { environment: 20, profile: 80, projectType: 80, location: 300, details: 8000,
  serviceDetails: 4000, timing: 80, access: 100, propertyType: 80, budget: 80,
  name: 100, contact: 254, preferredContact: 80, referral: 80, consent: 3, consentVersion: 100 };
export const CHOICES = {
  timing: ['Flexible', 'As soon as practical', 'I have a target date', 'Emergency — it cannot wait'],
  access: ['Not sure', 'Open — a machine can drive right to it', 'Tight — gates, fences, or landscaping in the way', 'Difficult — steep, wooded, or soft ground'],
  propertyType: ['Not specified', 'Residential', 'Acreage or farm', 'Commercial', 'New build site'],
  budget: ['Not sure yet', 'Under $5k', '$5k–$15k', '$15k–$40k', '$40k+'],
  preferredContact: ['No preference', 'Call', 'Text', 'Email'],
  referral: ['Not specified', 'Word of mouth', 'Google search or Maps', 'Saw the equipment on a job', 'Repeat customer'],
};
export function normalize(input, config) {
  const fail = (field, message) => { const error = new Error(message); error.field = field; throw error; };
  const result = {};
  for (const [key, limit] of Object.entries(LIMITS)) {
    const value = input[key];
    if (typeof value !== 'string' || value.length > limit || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)) fail(key, `Please check ${key}.`);
    if (!['details', 'serviceDetails'].includes(key) && /[\r\n]/.test(value)) fail(key, `Please check ${key}.`);
    result[key] = value.trim();
  }
  for (const key of ['location', 'details', 'contact']) if (!result[key]) fail(key, `Please complete ${key} before sending online.`);
  for (const [key, choices] of Object.entries(CHOICES)) if (!choices.includes(result[key])) fail(key, `Choose a listed ${key}.`);
  if (result.environment !== config.environment) fail('profile', 'This form and server use different environments. Use direct contact.');
  if (result.profile !== config.profile || !['', 'multiple', ...config.services].includes(result.projectType)) fail('projectType', 'This project form has changed. Copy your brief before reloading.');
  const email = /^[^\s@<>]+@[^\s@<>]+\.[^\s@<>]+$/.test(result.contact);
  const phone = /^[+()\d .-]+$/.test(result.contact) && /^\d{10,15}$/.test(result.contact.replace(/\D/g, ''));
  if ((!email && !phone) || (result.preferredContact === 'Email' && !email) ||
      (['Call', 'Text'].includes(result.preferredContact) && !phone)) fail('contact', 'Enter a usable phone number or email matching your preferred reply.');
  if (result.preferredContact === 'Text' && !config.supportsSMS) fail('preferredContact', 'Text replies are not enabled; choose another reply method.');
  if (result.consent !== 'yes') fail('consent', 'Please agree to send and store this project request.');
  if (result.consentVersion !== config.consentVersion) fail('consent', 'The privacy notice changed. Copy your brief before reloading.');
  return result;
}
export async function payloadHash(payload) {
  return [...new Uint8Array(await crypto.subtle.digest('SHA-256', new TextEncoder().encode(JSON.stringify(payload))))]
    .map(b => b.toString(16).padStart(2, '0')).join('');
}
export function validReceipt(receipt, attempt) {
  return receipt?.status === 'accepted' && receipt.id === attempt.id && receipt.hash === attempt.hash;
}
// Metadata only: never persist the brief or reply address without draft consent.
export function readAttempt(storage, key) {
  const raw = storage.getItem(key);
  if (!raw) return null;
  const record = JSON.parse(raw);
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i.test(record.id || '') ||
      !/^[0-9a-f]{64}$/.test(record.hash || '') || !['unknown','accepted','rejected'].includes(record.state)) throw new Error('Invalid submission metadata.');
  return { id: record.id, hash: record.hash, state: record.state };
}
const sending = new Set();
export async function submitRequest(payload, options) {
  const { storage, key, token, fetcher = fetch } = options;
  if (sending.has(key)) throw new Error('A request is already being sent.');
  sending.add(key);
  try {
    const hash = await payloadHash(payload);
    let attempt = readAttempt(storage, key);
    if (attempt && attempt.hash !== hash) throw new Error('These details differ from the earlier request. Retry the saved version or explicitly start a new request.');
    if (attempt?.state === 'accepted') return attempt;
    if (!token) throw new Error('Complete verification, then press Send or Retry again.');
    attempt = { id: attempt?.id || crypto.randomUUID(), hash, state: 'unknown' };
    // Fail before sending if identity cannot survive a reload.
    storage.setItem(key, JSON.stringify(attempt));
    if (storage.getItem(key) !== JSON.stringify(attempt)) throw new Error('Submission identity could not be saved. Use copy, download, or direct contact.');
    let response;
    try { response = await fetcher('/api/project-request', { method: 'POST',
      credentials: 'same-origin', signal: AbortSignal.timeout(18000),
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', Accept: 'application/json' },
      body: new URLSearchParams({ ...payload, 'submission-id': attempt.id, 'cf-turnstile-response': token }),
    }); } catch { throw new Error('Receipt is uncertain. Retry this same version to confirm it.'); }
    let body;
    try { body = await response.json(); } catch { throw new Error('Receipt is uncertain. Retry this same version to confirm it.'); }
    if (response.ok && validReceipt(body, attempt)) {
      attempt.state = 'accepted';
      // Receipt is still valid if storage is subsequently revoked. Keeping an
      // unknown marker also makes a reload retry safe against the same DB row.
      try { storage.setItem(key, JSON.stringify(attempt)); } catch { /* durable server receipt stands */ }
      return attempt;
    }
    if ([400,403,413,415,422].includes(response.status)) {
      attempt.state = 'rejected';
      storage.setItem(key, JSON.stringify(attempt));
      throw new Error(body?.error || 'The server rejected this request.');
    }
    throw new Error('Receipt is uncertain. Retry this same version to confirm it.');
  } finally { sending.delete(key); }
}
