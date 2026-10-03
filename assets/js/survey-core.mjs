import schema from '../contracts/survey-schema.json' with { type: 'json' };
export const FIELDS = schema.groups.flatMap(group => group.fields);
export const CHECKS = schema.checkChoices;
export const MAX_AGE = 7 * 24 * 60 * 60 * 1000;
export function emptyPacket() {
  return Object.fromEntries(FIELDS.map(field => [field.id, field.choices?.[0] || (field.type === 'check' ? CHECKS[0] : '')]));
}
// No expression evaluation, unit guessing, negative values or silent parseFloat truncation.
export function measurement(value, units = 'in') {
  if (value === '') return null;
  if (typeof value !== 'string' || value.length > 32) throw new Error('Use a short numeric measurement.');
  const text = value.trim();
  let result;
  if (/^(?:\d+(?:\.\d+)?|\.\d+)$/.test(text)) result = Number(text);
  else {
    const fraction = units === 'in' && /^(?:(\d+)\s+)?(\d+)\/(\d+)$/.exec(text);
    if (!fraction || Number(fraction[3]) === 0) throw new Error('Use a decimal, or an inch fraction such as 36 1/2.');
    result = Number(fraction[1] || 0) + Number(fraction[2]) / Number(fraction[3]);
  }
  if (!Number.isFinite(result) || result < 0 || result > 100000) throw new Error('Measurement must be between 0 and 100000.');
  return result;
}
export function validatePacket(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new Error('Packet fields must be an object.');
  const known = new Set(FIELDS.map(field => field.id));
  if (Object.keys(input).some(key => !known.has(key))) throw new Error('Packet contains unknown fields.');
  const result = emptyPacket();
  for (const field of FIELDS) {
    const value = Object.hasOwn(input, field.id) ? input[field.id] : result[field.id];
    if (typeof value !== 'string' || value.length > (field.limit || (['dimension','number'].includes(field.type) ? 32 : 100)) || /[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f]/.test(value)) throw new Error(`${field.label}: invalid or oversized value.`);
    if (field.type !== 'textarea' && /[\r\n]/.test(value)) throw new Error(`${field.label}: use one line.`);
    const choices = field.choices || (field.type === 'check' ? CHECKS : null);
    if (choices && !choices.includes(value)) throw new Error(`${field.label}: choose a listed value.`);
    if (field.type === 'date' && value && (!/^\d{4}-\d{2}-\d{2}$/.test(value) || !Number.isFinite(Date.parse(value)) || new Date(value).toISOString().slice(0,10) !== value)) throw new Error(`${field.label}: enter a valid date.`);
    result[field.id] = value;
  }
  for (const field of FIELDS.filter(field => ['dimension','number'].includes(field.type))) {
    try {
      const value = measurement(result[field.id], field.type === 'number' ? 'mm' : result.units);
      if (value === 0 && ['widthTop','widthMiddle','widthBottom','heightLeft','heightRight','doorWidth','doorHeight','thickness','weight','capacity','ceiling','railLength'].includes(field.id)) throw new Error('Enter a value greater than zero, or leave unknown values blank.');
    }
    catch (error) { throw new Error(`${field.label}: ${error.message}`); }
  }
  return result;
}
export function decodePacket(raw) {
  if (typeof raw !== 'string' || raw.length > 100000) throw new Error('Choose a survey JSON file smaller than 100 KB.');
  const packet = JSON.parse(raw);
  if (packet?.format !== 'jeff-door-survey' || packet.version !== schema.version) throw new Error('Unsupported survey file format or version.');
  return validatePacket(packet.fields);
}
export function encodePacket(fields, now = Date.now()) {
  return JSON.stringify({format:'jeff-door-survey', version:schema.version, savedAt:now, fields:validatePacket(fields)}, null, 2);
}
export function observations(input) {
  const p = validatePacket(input), result = [];
  const n = key => measurement(p[key], p.units);
  const fmt = value => `${Number(value.toFixed(3))} ${p.units}`;
  const has = keys => keys.every(key => p[key] !== '');
  if (p.configuration !== 'Single surface slider') return ['Pair, bypass and other arrangements require a separate geometry review; single-door calculations are disabled.'];
  const widths = ['widthTop','widthMiddle','widthBottom','overlapLeft','overlapRight','doorWidth'];
  if (has(widths)) {
    const required = Math.max(n('widthTop'), n('widthMiddle'), n('widthBottom')) + n('overlapLeft') + n('overlapRight');
    const margin = n('doorWidth') - required;
    result.push(`Width arithmetic: ${fmt(required)} clear-opening coverage plus entered overlaps; slab difference ${fmt(margin)}.${margin < 0 ? ' Proposed slab is smaller than the entered requirement.' : ' Confirm casing coverage and closed position separately.'}`);
  } else result.push('Width arithmetic unresolved: enter all three opening widths, both overlaps and slab width.');
  if (has(['ceiling','doorHeight','floorGap','headroom'])) {
    const available = n('ceiling') - n('doorHeight') - n('floorGap');
    result.push(`Headroom arithmetic: ${fmt(available)} above proposed slab top; manual requirement entered as ${fmt(n('headroom'))}.${available < n('headroom') ? ' Insufficient against the entered requirement.' : ' Confirm the manual uses this same datum.'}`);
  } else result.push('Headroom arithmetic unresolved: enter overhead height, slab height, floor gap and manual clearance above slab top.');
  if (has(['weight','capacity'])) {
    const weight = measurement(p.weight, 'mm'), capacity = measurement(p.capacity, 'mm');
    result.push(`Weight comparison: ${weight} ${p.weightUnit} against entered maximum ${capacity} ${p.weightUnit}.${weight > capacity ? ' Exceeds the entered maximum.' : ' Check minimum weight, slab fixings and every component rating separately.'}`);
  } else result.push('Weight comparison unresolved: obtain actual door weight and the documented system capacity.');
  result.push('Wall support, fixing design, wall gap, guide engagement, travel, access requirements and installation approval remain professional review items.');
  return result;
}
export function packetText(input) {
  const p = validatePacket(input);
  return ['DOOR SURVEY & JOB PACKET', `${p.job || 'Unnamed job'} / ${p.opening || 'Opening not identified'}`,
    'User-entered planning record. Not a quote, engineering approval or certification.',
    'All dimensions use one highest-finished-floor datum; see measurement notes.', '',
    ...schema.groups.flatMap(group => [group.title.toUpperCase(), ...group.fields.map(field => `${field.label}: ${p[field.id] || 'Not recorded'}`), '']),
    'CALCULATIONS & UNRESOLVED ITEMS', ...observations(p).map(item => `- ${item}`),
    ...(!p.manual || !p.specReviewedBy ? ['- Hardware manual and reviewer/date are not both recorded.'] : []),
    ...FIELDS.filter(field => field.type === 'check' && p[field.id] !== 'Recorded complete').map(field => `- ${field.label}: ${p[field.id]}`),
    '', 'Recheck measurements and the current manual before purchase or installation. Keep corrections with this packet.'].join('\n');
}
