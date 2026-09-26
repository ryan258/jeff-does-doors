import { LIMITS, normalize, payloadHash, readAttempt, submitRequest } from './intake-core.mjs';
let loading;
function loadChallenge() {
  if (window.turnstile) return Promise.resolve(window.turnstile);
  if (loading) return loading;
  loading = new Promise((resolve, reject) => {
    const script = document.createElement('script');
    const timer = setTimeout(() => fail(), 12000);
    const fail = () => { clearTimeout(timer); script.remove(); loading = null; reject(new Error('Verification did not load. Try again, or use the direct contact options.')); };
    script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit';
    script.async = true; script.onerror = fail;
    script.onload = () => { clearTimeout(timer); if (window.turnstile) resolve(window.turnstile); else fail(); };
    document.head.append(script);
  });
  return loading;
}
for (const form of document.querySelectorAll('[data-online-intake]')) {
  const panel = form.querySelector('[data-online-panel]');
  const send = panel.querySelector('[data-send-request]');
  const retry = panel.querySelector('[data-retry-request]');
  const restart = panel.querySelector('[data-new-request]');
  const status = panel.querySelector('[data-request-status]');
  const revision = panel.querySelector('[data-request-revision]');
  const consent = panel.querySelector('[data-request-consent]');
  const challengeStatus = panel.querySelector('[data-challenge-status]');
  const config = { environment: panel.dataset.environment, profile: form.dataset.profileId, services: [...form.elements.namedItem('projectType').options].map(o => o.dataset.serviceId),
    supportsSMS: form.dataset.supportsSms === 'true', consentVersion: panel.dataset.consentVersion };
  const key = `construction-submission:v1:${config.profile}:${form.dataset.draftScope}`;
  let token = '', widget, snapshot, busy = false, confirmed = false;
  function message(text) { status.textContent = text; }
  function reveal(fieldName) {
    const field = fieldName === 'consent' ? consent : form.elements.namedItem(fieldName);
    if (!field) return;
    field.closest('details')?.setAttribute('open', '');
    form.dispatchEvent(new CustomEvent('brief:reveal-field', { detail: fieldName }));
    field.focus();
  }
  async function perform(useSnapshot) {
    if (busy) return;
    busy = true; send.disabled = true; retry.disabled = true;
    try {
      const storage = window.sessionStorage;
      let payload = snapshot;
      if (!useSnapshot) {
        const values = Object.fromEntries(Object.keys(LIMITS).map(key => [key, form.elements.namedItem(key)?.value || '']));
        values.projectType = form.elements.namedItem('projectType').selectedOptions[0]?.dataset.serviceId || '';
        values.environment = config.environment; values.profile = config.profile; values.consent = consent.checked ? 'yes' : '';
        values.consentVersion = config.consentVersion;
        try { payload = normalize(values, config); } catch (error) { reveal(error.field); throw error; }
      }
      if (!payload) throw new Error('Restore or re-enter the earlier details, or explicitly start a new request.');
      const prior = readAttempt(storage, key);
      if (snapshot && !prior) throw new Error('The earlier request identity is missing. Use Start a new request to acknowledge possible duplication before sending again.');
      if (prior && prior.hash !== await payloadHash(payload)) throw new Error('These details differ from the earlier request. Retry the submitted version or explicitly start a new request.');
      message('Loading verification… Your request has not been sent by this action.');
      const challenge = await loadChallenge();
      if (widget === undefined) widget = challenge.render(panel.querySelector('[data-request-challenge]'), {
        sitekey: panel.dataset.siteKey, action: 'project-request', 'response-field': false,
        callback: value => { token = value; if (!confirmed) challengeStatus.textContent = ('Verification ready. Press Send or Retry to continue.'); },
        'expired-callback': () => { token = ''; if (!confirmed) challengeStatus.textContent = ('Verification expired. Complete it again before sending.'); },
        'error-callback': () => { token = ''; if (!confirmed) challengeStatus.textContent = ('Verification failed. Try again or use direct contact.'); },
      });
      if (!token) throw new Error('Complete verification, then press Send or Retry again.');
      message('Sending… Keep this page open until a receipt is confirmed.');
      // Preserve the exact submitted revision, including if fields change during fetch.
      snapshot = payload;
      revision.textContent = Object.entries(snapshot).filter(([k]) => !['consent','consentVersion','profile'].includes(k)).map(([k,v]) => `${k}: ${v || 'Not specified'}`).join('\n');
      revision.parentElement.hidden = false;
      const receipt = await submitRequest(payload, { storage, key, token });
      snapshot = payload; confirmed = true;
      message(`Saved successfully. Receipt: ${receipt.id}. This confirms storage, not a booking or an email delivery. Your submitted version is shown below.`);
      retry.hidden = true; restart.hidden = false;
    } catch (error) {
      message(`${error.message} Your brief remains available to copy or download.`);
      try { const prior = readAttempt(window.sessionStorage, key); retry.hidden = !snapshot || !prior || prior.state === 'accepted'; restart.hidden = !prior && !snapshot; } catch { restart.hidden = false; }
    } finally {
      token = ''; if (!confirmed && widget !== undefined) window.turnstile?.reset(widget);
      busy = false; send.disabled = confirmed; retry.disabled = false;
    }
  }
  send.addEventListener('click', () => perform(false));
  retry.addEventListener('click', () => perform(true));
  restart.addEventListener('click', () => {
    if (busy || !window.confirm('A previous request may already have been saved. Starting a new request can create a second inquiry. Continue?')) return;
    try { window.sessionStorage.removeItem(key); snapshot = undefined; confirmed = false; send.disabled = false; if (widget !== undefined) window.turnstile?.reset(widget); retry.hidden = true; restart.hidden = true; revision.parentElement.hidden = true; consent.checked = false; message('New request ready. Review the current details and consent before sending.'); }
    catch { message('Submission storage is unavailable. Use copy, download, or direct contact.'); }
  });
  try {
    const prior = readAttempt(window.sessionStorage, key);
    if (prior) { confirmed = prior.state === 'accepted'; restart.hidden = false; message(`Earlier request ${prior.id}: ${prior.state}. Restore the same brief to confirm or retry it, or explicitly start a new request.`); }
  } catch { message('Submission storage is unavailable. Use copy, download, or direct contact.'); }
  send.disabled = confirmed;
}
