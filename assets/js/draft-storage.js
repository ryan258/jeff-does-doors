/* Optional device storage. No network calls; malformed/expired records never restore. */
(function (root) {
  'use strict';
  const MAX_AGE = 7 * 24 * 60 * 60 * 1000;
  const fields = ['projectType', 'location', 'details', 'serviceDetails', 'timing', 'access', 'propertyType', 'budget', 'name', 'contact', 'preferredContact', 'referral'];
  const validFields = (value) => value && typeof value === 'object' && !Array.isArray(value)
    && Object.keys(value).every((key) => fields.includes(key) && typeof value[key] === 'string' && value[key].length <= 10000);
  const decode = (raw, now = Date.now()) => {
    try {
      const value = JSON.parse(raw);
      if (value?.version !== 1 || !Number.isFinite(value.savedAt) || value.savedAt > now
        || now - value.savedAt >= MAX_AGE || !validFields(value.fields)) return null;
      return value;
    } catch { return null; }
  };
  const read = (storage, key, now = Date.now()) => {
    try {
      const raw = storage.getItem(key);
      const record = decode(raw, now);
      if (raw && !record) storage.removeItem(key);
      return { available: true, record };
    } catch { return { available: false, record: null }; }
  };
  const save = (storage, key, values, now = Date.now()) => {
    if (!validFields(values)) return { saved: false };
    const record = { version: 1, savedAt: now, fields: values };
    try { storage.setItem(key, JSON.stringify(record)); return { saved: true, record }; }
    catch { return { saved: false }; }
  };
  const remove = (storage, key) => {
    try { storage.removeItem(key); return true; } catch { return false; }
  };
  const api = { fields, decode, read, save, remove, MAX_AGE };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ConstructionDrafts = api;
})(typeof window !== 'undefined' ? window : this);
