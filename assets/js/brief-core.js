/* Pure helpers shared by the browser bundle and focused Node tests. */
(function (root) {
  'use strict';
  const validEntry = (entry) => entry && typeof entry === 'object'
    && ['title', 'url', 'summary', 'text', 'section'].every((key) => typeof entry[key] === 'string')
    && entry.title.trim() && /^\/(?!\/)/.test(entry.url);
  const validIndex = (entries) => Array.isArray(entries) && entries.every(validEntry);
  const scoreEntry = (entry, needle) => ['title', 'summary', 'text'].reduce((score, key, index) =>
    score + (entry[key].toLowerCase().includes(needle) ? [10, 3, 1][index] : 0), 0);
  const api = { validIndex, scoreEntry };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  else root.ConstructionBrief = api;
})(typeof window !== 'undefined' ? window : this);
