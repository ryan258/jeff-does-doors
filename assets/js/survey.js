import { FIELDS, MAX_AGE, measurement, emptyPacket, validatePacket, decodePacket, encodePacket, packetText } from './survey-core.mjs';
const form = document.querySelector('[data-survey]');
if (form) {
  const find = name => form.querySelector(`[data-survey-${name}]`);
  const state = find('status'), save = find('save');
  const result = document.querySelector('[data-survey-result]'), output = document.querySelector('[data-survey-output]');
  const key = `door-survey:v1:${form.dataset.profile}:${form.dataset.scope}`;
  let storage, revision = 0, previousUnits = 'in', previousWeightUnit = 'lb';
  try { storage = window.localStorage; } catch { /* exporting is still available */ }
  const say = text => { state.textContent = text; };
  const collect = () => validatePacket(Object.fromEntries(FIELDS.map(field => [field.id, form.elements.namedItem(field.id).value])));
  const populate = packet => { for (const field of FIELDS) form.elements.namedItem(field.id).value = packet[field.id]; previousUnits = packet.units; previousWeightUnit = packet.weightUnit; revision++; result.hidden = true; };
  const guard = action => { try { action(); } catch (error) { say(`${error.message} The current fields are still available. Copy or export valid entries before leaving.`); } };
  const saveCurrent = () => {
    if (!save.checked) return;
    const raw = encodePacket(collect());
    if (!storage) throw new Error('Device saving is unavailable.');
    storage.setItem(key, raw);
    if (storage.getItem(key) !== raw) throw new Error('Device saving could not be confirmed.');
    find('restore').hidden = true;
    say('Saved on this device for seven days. Nothing was sent.');
  };
  const readSaved = () => {
    const raw = storage?.getItem(key);
    if (!raw) return null;
    const record = JSON.parse(raw);
    if (!Number.isFinite(record.savedAt) || record.savedAt > Date.now() || Date.now() - record.savedAt >= MAX_AGE) { storage.removeItem(key); return null; }
    return decodePacket(raw);
  };
  const prepare = () => { const packet = collect(); output.textContent = packetText(packet); result.hidden = false; return packet; };
  const download = (text, extension, type) => {
    const url = URL.createObjectURL(new Blob([text], {type}));
    const anchor = document.createElement('a'); anchor.href = url; anchor.download = `door-survey.${extension}`; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000); say('Download requested. Check your downloads; nothing was sent.');
  };
  for (const element of form.querySelectorAll('[disabled]')) element.disabled = false;
  guard(() => { find('restore').hidden = !readSaved(); });
  const changed = event => {
    if (!event.target.name) return;
    // Unit selectors use change only so the old unit remains known during conversion.
    if (['units','weightUnit'].includes(event.target.name) && event.type === 'input') return;
    revision++; result.hidden = true;
    guard(() => {
      const isDimension = event.target.name === 'units';
      if (isDimension || event.target.name === 'weightUnit') {
        const before = isDimension ? previousUnits : previousWeightUnit;
        const after = event.target.value;
        if (before !== after) {
          const factor = isDimension ? (after === 'mm' ? 25.4 : 1 / 25.4) : (after === 'kg' ? 0.45359237 : 1 / 0.45359237);
          const fields = FIELDS.filter(field => isDimension ? field.type === 'dimension' : ['weight','capacity'].includes(field.id));
          let converted;
          try {
            converted = fields.map(field => {
              const input = form.elements.namedItem(field.id);
              const value = input.value === '' ? '' : String(Number((measurement(input.value, isDimension ? before : 'mm') * factor).toFixed(6)));
              if (value) measurement(value, 'mm');
              return [input, value];
            });
          } catch (error) { event.target.value = before; throw error; }
          for (const [input, value] of converted) input.value = value;
          if (isDimension) previousUnits = after; else previousWeightUnit = after;
          say(`Existing values converted from ${before} to ${after}, rounded to six decimals. Review the measurements.`);
        }
      }
      saveCurrent();
    });
  };
  form.addEventListener('input', changed);
  form.addEventListener('change', changed);
  save.addEventListener('change', () => guard(() => {
    if (save.checked) {
      if (!find('restore').hidden && !window.confirm('Replace the saved packet with these current fields?')) { save.checked = false; return; }
      saveCurrent();
    } else {
      if (!storage) throw new Error('Device storage is unavailable.');
      storage.removeItem(key); find('restore').hidden = true; say('Device copy deleted; the current fields remain.');
    }
  }));
  find('restore').addEventListener('click', () => guard(() => {
    const packet = readSaved();
    if (!packet) { find('restore').hidden = true; say('No unexpired saved packet remains.'); return; }
    if (!window.confirm('Replace the current fields with the saved packet? Export current work first if you need it.')) return;
    populate(packet); save.checked = true; find('restore').hidden = true; say('Saved packet restored. Review the date and specifications.');
  }));
  find('delete').addEventListener('click', () => guard(() => {
    if (!storage) throw new Error('Device storage is unavailable.');
    storage.removeItem(key); save.checked = false; find('restore').hidden = true; say('Device copy deleted. Current fields remain until you leave or start a new opening.');
  }));
  find('import').addEventListener('change', async event => {
    const file = event.target.files?.[0], before = revision;
    if (!file) return;
    try {
      if (file.size > 100000) throw new Error('Choose a survey JSON file smaller than 100 KB.');
      const packet = decodePacket(await file.text());
      if (revision !== before) throw new Error('Fields changed while the file loaded. Import again to avoid overwriting newer work.');
      if (!window.confirm('Replace current fields with this imported packet? Export current work first if needed.')) return;
      save.checked = false; populate(packet);
      try { find('restore').hidden = !readSaved(); } catch { find('restore').hidden = true; }
      say('Imported into this page. Device saving is off; any earlier device copy is unchanged.');
    } catch (error) { say(`Import stopped: ${error.message}`); }
    finally { event.target.value = ''; }
  });
  form.addEventListener('submit', event => { event.preventDefault(); guard(() => { prepare(); result.focus(); say('Packet prepared. Review unresolved items before sharing.'); }); });
  find('json').addEventListener('click', () => guard(() => download(encodePacket(prepare()), 'json', 'application/json')));
  find('text').addEventListener('click', () => guard(() => { prepare(); download(output.textContent, 'txt', 'text/plain;charset=utf-8'); }));
  find('copy').addEventListener('click', async () => {
    try { prepare(); } catch (error) { say(error.message); return; }
    try { await navigator.clipboard.writeText(output.textContent); say('Packet copied.'); }
    catch { say('Copy is unavailable. Use Download text to keep the packet without selecting text.'); }
  });
  window.addEventListener('beforeprint', () => {
    try { prepare(); }
    catch (error) { output.textContent = `Packet cannot be prepared: ${error.message}\nCorrect the current fields before printing.`; result.hidden = false; }
  });
  find('print').addEventListener('click', () => guard(() => { prepare(); window.print(); }));
  find('new').addEventListener('click', () => {
    if (!window.confirm('Start another opening? Current unsaved entries will be cleared. Export this packet first if needed. The device copy will remain until replaced or deleted.')) return;
    guard(() => { save.checked = false; populate(emptyPacket()); find('restore').hidden = !readSaved(); say('New opening ready. Device saving is off.'); form.elements.namedItem('job').focus(); });
  });
}
