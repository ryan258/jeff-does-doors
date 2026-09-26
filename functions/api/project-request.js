import { IntakeError, parseForm, reply, runtime, saveInquiry, validate, verifyToken } from '../../lib/intake.mjs';
import { deliver } from '../../lib/notifications.mjs';
export async function onRequest({ request, env, waitUntil }) {
  if (request.method !== 'POST') return reply(405, { error: 'Use POST.' }, { Allow: 'POST' });
  try {
    const hosts = runtime(env, request);
    const data = await parseForm(request);
    const payload = validate(data, env);
    await verifyToken(data, env, hosts);
    const receipt = await saveInquiry(env.DB, data['submission-id'], payload);
    try { waitUntil(deliver(env, receipt.id).catch(() => console.error('notification_recovery_required'))); }
    catch { console.error('notification_not_scheduled'); }
    return reply(200, { status: 'accepted', ...receipt });
  } catch (error) {
    if (error instanceof IntakeError) return reply(error.status, { error: error.message });
    console.error('intake_unavailable');
    return reply(503, { error: 'Receipt is uncertain. Retry the same request to confirm it.' });
  }
}
