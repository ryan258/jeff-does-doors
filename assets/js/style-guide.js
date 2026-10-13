/* Guide-only enhancement. Every specimen and native control works without it. */
(() => {
  'use strict';
  const guide = document.querySelector('[data-component-guide]');
  if (!guide) return;
  const search = guide.querySelector('[data-guide-search]');
  const family = guide.querySelector('[data-guide-family]');
  const count = guide.querySelector('[data-guide-count]');
  const empty = guide.querySelector('[data-guide-empty]');
  const entries = Array.from(guide.querySelectorAll('[data-guide-entry]'));
  if (!search || !family || !count || !empty) return;

  const filter = () => {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    entries.forEach((entry) => {
      const text = entry.dataset.guideSearchText.toLocaleLowerCase();
      const matches = (family.value === 'all' || entry.dataset.guideFamilyName === family.value)
        && terms.every((term) => text.includes(term));
      entry.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = `${visible} of ${entries.length} components`;
    empty.hidden = visible !== 0;
  };
  const reset = () => { search.value = ''; family.value = 'all'; filter(); };
  const resetAndFocus = () => { reset(); search.focus(); };
  const revealHash = () => {
    let id;
    try { id = decodeURIComponent(window.location.hash.slice(1)); } catch { return; }
    const entry = entries.find((item) => item.id === id);
    if (!entry) return;
    if (entry.hidden) reset();
    // A hash is a DOM id, never a selector or HTML. Direct specimen links also
    // work when arriving with browser-restored filter values.
    entry.scrollIntoView({ block: 'start', behavior: 'instant' });
  };
  search.addEventListener('input', filter);
  family.addEventListener('change', filter);
  guide.querySelector('[data-guide-reset]').addEventListener('click', resetAndFocus);
  guide.querySelector('[data-guide-empty-reset]').addEventListener('click', resetAndFocus);
  window.addEventListener('hashchange', revealHash);
  // Re-clicking the current fragment produces no hashchange event.
  guide.querySelectorAll('a[href^="#component-"]').forEach((link) => {
    link.addEventListener('click', () => {
      const target = entries.find((entry) => `#${entry.id}` === link.getAttribute('href'));
      if (target && target.hidden) reset();
    });
  });
  filter();
  guide.querySelector('[data-guide-controls]').hidden = false;
  revealHash();

  const copyStatus = guide.querySelector('[data-guide-copy-status]');
  if (navigator.clipboard && typeof navigator.clipboard.writeText === 'function') {
    guide.querySelectorAll('[data-guide-copy]').forEach((button) => {
      button.hidden = false;
      button.addEventListener('click', async () => {
        const source = document.getElementById(button.dataset.guideCopy);
        if (!source) return;
        try {
          await navigator.clipboard.writeText(source.textContent);
          copyStatus.textContent = 'Usage snippet copied.';
        } catch {
          source.focus();
          const selection = window.getSelection();
          const range = document.createRange();
          range.selectNodeContents(source);
          selection.removeAllRanges();
          selection.addRange(range);
          copyStatus.textContent = 'Clipboard unavailable. The snippet is selected for manual copying.';
        }
      });
    });
  }
})();
