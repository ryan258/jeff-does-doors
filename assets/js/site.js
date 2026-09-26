(() => {
  'use strict';

  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => Array.from(scope.querySelectorAll(selector));
  const initialize = (name, setup) => {
    try { setup(); } catch (error) { console.error(`Unable to initialize ${name}`, error); }
  };
  const reducedMotion = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  // Shared: both the gallery and filter closures bind against this grid.
  const galleryGrid = $('[data-gallery]');

  initialize('navigation', () => {
  // --- Mobile navigation -----------------------------------------------------
  const mobileNav = $('.site-header__mobile-nav');
  if (mobileNav) {
    $$('a', mobileNav).forEach((link) => link.addEventListener('click', () => mobileNav.removeAttribute('open')));
  }

  });

  initialize('dropdowns', () => {
    const groups = $$('[data-nav-disclosure]');
    const close = (group, restore = false) => {
      const button = $('[data-nav-toggle]', group);
      button.setAttribute('aria-expanded', 'false');
      $('[data-nav-panel]', group).hidden = true;
      if (restore) button.focus();
    };
    groups.forEach((group) => {
      const button = $('[data-nav-toggle]', group);
      const panel = $('[data-nav-panel]', group);
      button.hidden = false;
      panel.hidden = true;
      button.addEventListener('click', () => {
        const opening = button.getAttribute('aria-expanded') !== 'true';
        groups.forEach((other) => close(other));
        button.setAttribute('aria-expanded', String(opening));
        panel.hidden = !opening;
      });
      group.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') { event.preventDefault(); close(group, true); }
      });
      group.addEventListener('focusout', (event) => {
        if (!group.contains(event.relatedTarget)) close(group);
      });
    });
    document.addEventListener('click', (event) => groups.forEach((group) => {
      if (!group.contains(event.target)) close(group);
    }));
  });

  initialize('announcement', () => {
  // --- Announcement bar ------------------------------------------------------
  // Stores only this announcement dismissal on this device.
  const promo = $('[data-promo]');
  if (promo) {
    const key = `jc-promo-dismissed:${promo.textContent.trim().slice(0, 60)}`;
    let dismissed = false;
    try { dismissed = localStorage.getItem(key) === '1'; } catch { dismissed = false; }
    // The header overlays the hero, so it has to shift down by however tall
    // the bar actually renders — one line on desktop, two when it wraps.
    const publishHeight = () => {
      document.documentElement.style.setProperty('--promo-h', promo.hidden ? '0px' : `${promo.offsetHeight}px`);
    };
    promo.hidden = dismissed;
    publishHeight();
    window.addEventListener('resize', publishHeight);
    $('[data-promo-dismiss]', promo)?.addEventListener('click', () => {
      promo.hidden = true;
      publishHeight();
      try { localStorage.setItem(key, '1'); } catch { /* private browsing */ }
    });
  }

  });

  initialize('gallery', () => {
  // --- Photo gallery + lightbox ---------------------------------------------
  const lightbox = $('[data-lightbox]');
  if (galleryGrid && lightbox && typeof lightbox.showModal === 'function') {
    const cells = $$('[data-gallery-open]', galleryGrid);
    const image = $('[data-lightbox-image]', lightbox);
    const caption = $('[data-lightbox-caption]', lightbox);
    let activeIndex = 0;

    const getVisibleShots = () => {
      return cells
        .filter((button) => !button.closest('[hidden]'))
        .map((button) => {
          const img = $('img', button);
          return {
            button,
            src: button.getAttribute('href') || img.getAttribute('src'),
            alt: img.getAttribute('alt'),
            caption: $('strong', button)?.textContent || '',
          };
        });
    };

    const prevBtn = $('[data-lightbox-prev]', lightbox);
    const nextBtn = $('[data-lightbox-next]', lightbox);

    const show = (next) => {
      const visible = getVisibleShots();
      if (!visible.length) return;
      activeIndex = (next + visible.length) % visible.length;
      image.src = visible[activeIndex].src;
      image.alt = visible[activeIndex].alt;
      caption.textContent = visible[activeIndex].caption;
      const multi = visible.length > 1;
      if (prevBtn) prevBtn.hidden = !multi;
      if (nextBtn) nextBtn.hidden = !multi;
    };

    cells.forEach((button) => {
      button.addEventListener('click', (event) => {
        event.preventDefault();
        const visible = getVisibleShots();
        const pos = visible.findIndex((item) => item.button === button);
        if (pos !== -1) {
          show(pos);
          lightbox.showModal();
        }
      });
    });

    $('[data-lightbox-close]', lightbox)?.addEventListener('click', () => lightbox.close());
    prevBtn?.addEventListener('click', () => show(activeIndex - 1));
    nextBtn?.addEventListener('click', () => show(activeIndex + 1));
    lightbox.addEventListener('keydown', (event) => {
      if (event.key === 'ArrowLeft') show(activeIndex - 1);
      if (event.key === 'ArrowRight') show(activeIndex + 1);
    });
    lightbox.addEventListener('click', (event) => {
      if (event.target === lightbox) lightbox.close();
    });
  }

  });

  initialize('filters', () => {
  // --- Filter buttons (gallery tags, blog categories) ------------------------
  const wireFilter = (attribute, itemAttribute, container) => {
    const buttons = $$(`[${attribute}]`);
    if (!buttons.length || !container) return;
    buttons.forEach((button) => {
      button.addEventListener('click', () => {
        const value = button.getAttribute(attribute);
        buttons.forEach((other) => other.setAttribute('aria-pressed', String(other === button)));
        $$(`[${itemAttribute}]`, container).forEach((item) => {
          item.hidden = value !== 'all' && item.getAttribute(itemAttribute) !== value;
        });
      });
    });
  };
  wireFilter('data-gallery-filter', 'data-gallery-tag', galleryGrid);
  wireFilter('data-post-filter', 'data-post-category', $('[data-post-list]'));

  });

  initialize('comparison', () => {
  // --- Before / after comparison --------------------------------------------
  $$('[data-before-after]').forEach((widget) => {
    const clip = $('[data-before-after-clip]', widget);
    const range = $('[data-before-after-range]', widget);
    if (!clip || !range) return;
    const apply = () => widget.style.setProperty('--split', `${range.value}%`);
    range.disabled = false;
    range.addEventListener('input', apply);
    apply();
  });

  });

  initialize('search', () => {
  // --- Site search -----------------------------------------------------------
  const searchDialog = $('[data-search-dialog]');
  if (searchDialog && typeof searchDialog.showModal === 'function') {
    const input = $('[data-search-input]', searchDialog);
    const results = $('[data-search-results]', searchDialog);
    const hint = $('[data-search-hint]', searchDialog);
    const indexURL = document.body.dataset.searchIndex;
    let entries = null;
    let loadState = 'idle';

    const load = async () => {
      if (loadState === 'success' && entries) return entries;
      if (loadState === 'loading') return null;
      loadState = 'loading';
      hint.textContent = 'Loading search index…';
      try {
        const response = await fetch(indexURL);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        if (!window.ConstructionBrief.validIndex(data)) throw new Error('Malformed index');
        entries = data;
        loadState = 'success';
      } catch {
        entries = null;
        loadState = 'error';
        hint.textContent = 'Search is unavailable right now. Use the menu instead.';
      }
      return entries;
    };

    const search = (term) => {
      if (loadState === 'error') {
        hint.textContent = 'Search is unavailable right now. Use the menu instead.';
        results.innerHTML = '';
        return;
      }
      if (loadState === 'loading') {
        hint.textContent = 'Loading search index…';
        results.innerHTML = '';
        return;
      }
      const needle = term.trim().toLowerCase();
      results.innerHTML = '';
      if (needle.length < 2) {
        hint.textContent = 'Type to search. Results appear as you type.';
        return;
      }
      if (!entries) return;

      const matches = entries
        .map((entry) => {
          const score = window.ConstructionBrief.scoreEntry(entry, needle);
          return { entry, score };
        })
        .filter((item) => item.score > 0)
        .sort((a, b) => b.score - a.score)
        .map((item) => item.entry)
        .slice(0, 12);

      hint.textContent = matches.length ? `${matches.length} result${matches.length === 1 ? '' : 's'}` : 'No matches. Try a different word.';
      matches.forEach((entry) => {
        const item = document.createElement('li');
        const link = document.createElement('a');
        link.href = entry.url;
        link.innerHTML = `<strong></strong><small></small>`;
        link.querySelector('strong').textContent = entry.title;
        link.querySelector('small').textContent = entry.summary || entry.section;
        item.append(link);
        results.append(item);
      });
    };

    const open = async () => {
      if (!searchDialog.open) searchDialog.showModal();
      input.focus();
      await load();
      search(input.value);
    };

    $$('[data-search-open]').forEach((button) => button.addEventListener('click', open));
    $('[data-search-close]', searchDialog)?.addEventListener('click', () => searchDialog.close());
    input?.addEventListener('input', () => search(input.value));
    searchDialog.addEventListener('click', (event) => {
      if (event.target === searchDialog) searchDialog.close();
    });
    document.addEventListener('keydown', (event) => {
      if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey && !document.activeElement?.isContentEditable && !document.querySelector('dialog[open]') && !/^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '')) {
        event.preventDefault();
        open();
      }
    });
  }

  });

  initialize('brief', () => {
  // --- Project brief builder -------------------------------------------------
  $$('[data-project-form]').forEach((briefForm) => {
    const result = $('[data-brief-result]', briefForm);
    const briefTextElement = $('[data-brief-text]', briefForm);
    const status = $('[data-brief-status]', briefForm);
    const copyButton = $('[data-copy-brief]', briefForm);
    const downloadButton = $('[data-download-brief]', briefForm);
    const emailLink = $('[data-brief-email]', briefForm);
    const smsLink = $('[data-brief-sms]', briefForm);
    const callLink = $('[data-brief-call]', briefForm);
    const contactEmail = (briefForm.dataset.contactEmail || '').trim();
    const contactPhone = (briefForm.dataset.contactPhone || '').trim();
    const contactTel = contactPhone.replace(/[^0-9+]/g, '');
    const companyName = briefForm.dataset.companyName || 'the contractor';
    const supportsSMS = briefForm.dataset.supportsSms === 'true';
    let latestBrief = '';

    const valueFor = (name, fallback) => {
      const field = briefForm.elements.namedItem(name);
      return field && field.value.trim() ? field.value.trim() : fallback;
    };

    const setHandoffLink = (link, href, hidden) => {
      if (!link) return;
      link.hidden = hidden;
      if (hidden) link.removeAttribute('href');
      else link.href = href;
    };

    const updateHandoffLinks = () => {
      const subject = `Project inquiry: ${valueFor('projectType', 'Project discussion')}`;
      const encodedBrief = encodeURIComponent(latestBrief);
      setHandoffLink(emailLink, `mailto:${contactEmail}?subject=${encodeURIComponent(subject)}&body=${encodedBrief}`, !contactEmail);
      setHandoffLink(smsLink, `sms:${contactTel}?body=${encodedBrief}`, !contactTel || !supportsSMS);
      setHandoffLink(callLink, `tel:${contactTel}`, !contactTel);
    };

    // Optional field: only printed when the form actually has it.
    const optionalLine = (label, name) => {
      const field = briefForm.elements.namedItem(name);
      return field ? [`${label}: ${valueFor(name, 'Not specified')}`] : [];
    };

    const buildBrief = () => [
      `Project inquiry for ${companyName}`,
      '',
      `Work: ${valueFor('projectType', 'Not specified yet')}`,
      ...optionalLine('Starting point', 'startingPoint'),
      `Property / area: ${valueFor('location', 'Not specified yet')}`,
      ...optionalLine('Service details', 'serviceDetails'),
      ...optionalLine('Property type', 'propertyType'),
      ...optionalLine('Door access', 'access'),
      `Timing: ${valueFor('timing', 'Flexible')}`,
      ...optionalLine('Budget range', 'budget'),
      `Preferred reply: ${valueFor('preferredContact', 'No preference')}`,
      `Name: ${valueFor('name', 'Not provided')}`,
      `Best phone or email: ${valueFor('contact', 'Not provided')}`,
      ...optionalLine('Heard about us via', 'referral'),
      '',
      'What needs attention:',
      valueFor('details', 'I would like to talk through the project.'),
    ].join('\n');

    // --- Multi-step wizard (estimate page only) ------------------------------
    const steps = $$('[data-wizard-step]', briefForm);
    const isWizard = briefForm.hasAttribute('data-wizard') && steps.length > 1;
    const nextButton = $('[data-wizard-next]', briefForm);
    const backButton = $('[data-wizard-back]', briefForm);
    const submitButton = $('[data-brief-submit]', briefForm);
    const progress = $('[data-wizard-progress]', briefForm);
    let step = 0;

    // Enable interactive controls now that JavaScript is initialized (Finding 2)
    if (submitButton) submitButton.disabled = false;
    if (nextButton) nextButton.disabled = false;

    const renderStep = () => {
      steps.forEach((panel, position) => { panel.hidden = position !== step; });
      if (backButton) backButton.hidden = step === 0;
      if (nextButton) nextButton.hidden = step === steps.length - 1;
      if (submitButton) submitButton.hidden = step !== steps.length - 1;
      if (progress) progress.textContent = `Step ${step + 1} of ${steps.length}`;
      if (submitButton) submitButton.disabled = step !== steps.length - 1;
    };

    if (isWizard) {
      renderStep();
      nextButton?.addEventListener('click', () => {
        const invalid = $$('input, select, textarea', steps[step]).find((field) => !field.checkValidity());
        if (invalid) { invalid.reportValidity(); return; }
        step = Math.min(step + 1, steps.length - 1);
        renderStep();
        steps[step].querySelector('[data-step-heading], input, select, textarea')?.focus();
      });
      backButton?.addEventListener('click', () => {
        step = Math.max(step - 1, 0);
        renderStep();
        steps[step].querySelector('[data-step-heading], input, select, textarea')?.focus();
      });
    }

    briefForm.addEventListener('brief:reveal-field', (event) => {
      const field = briefForm.elements.namedItem(event.detail);
      if (isWizard && field) {
        const index = steps.findIndex(panel => panel.contains(field));
        if (index >= 0) { step = index; renderStep(); }
      }
    });

    const preselectService = () => {
      const select = briefForm.elements.namedItem('projectType');
      const serviceId = new URLSearchParams(window.location.search).get('service');
      if (!select || !serviceId) return;
      const option = Array.from(select.options).find((item) => item.dataset.serviceId === serviceId);
      if (option) select.value = option.value;
    };
    const serviceSelect = briefForm.elements.namedItem('projectType');
    const serviceDetail = $('[data-service-detail]', briefForm);
    const servicePrompt = $('[data-service-prompt]', briefForm);
    const showServicePrompt = () => {
      const prompt = serviceSelect?.selectedOptions[0]?.dataset.inquiryPrompt || '';
      if (serviceDetail) serviceDetail.hidden = !prompt;
      if (servicePrompt) servicePrompt.textContent = prompt + ' (optional)';
    };
    serviceSelect?.addEventListener('change', () => {
      const detail = briefForm.elements.namedItem('serviceDetails');
      if (detail) detail.value = '';
      showServicePrompt();
    });
    preselectService();
    showServicePrompt();

    const syncBrief = () => {
      latestBrief = buildBrief();
      briefTextElement.textContent = latestBrief;
      updateHandoffLinks();
    };

    // Explicit opt-in storage is scoped to this business and site path.
    // Merely finding an old draft never restores it over the visitor's current input.
    const recovery = $('[data-draft-recovery]', briefForm);
    const store = window.ConstructionDrafts;
    if (recovery && store) {
      recovery.hidden = false;
      const consent = $('[data-draft-consent]', recovery);
      const restore = $('[data-draft-restore]', recovery);
      const discard = $('[data-draft-discard]', recovery);
      const state = $('[data-draft-state]', recovery);
      const key = `construction-draft:v1:${briefForm.dataset.profileId}:${briefForm.dataset.draftScope}`;
      let storage;
      try { storage = window.localStorage; } catch { storage = null; }
      let saved = store.read(storage, key);
      const describe = (record, prefix) => `${prefix} ${new Date(record.savedAt).toLocaleString()}. Expires after 7 days. Device saving does not send it.`;
      const offer = () => {
        restore.hidden = !saved.record;
        state.textContent = !saved.available ? 'Device saving is unavailable. Copy or download your message.'
          : saved.record ? describe(saved.record, 'Saved draft available from') : 'Not saved on this device.';
      };
      offer();
      const save = () => {
        if (!consent.checked) return;
        const values = Object.fromEntries(store.fields.map((name) => [name, briefForm.elements.namedItem(name)?.value || '']));
        const result = store.save(storage, key, values);
        if (result.saved) {
          saved = { available: true, record: result.record };
          state.textContent = describe(result.record, 'Saved on this device at');
          restore.hidden = true;
        } else state.textContent = 'Changes could not be saved. Copy or download before leaving.';
      };
      const clear = () => {
        consent.checked = false;
        if (store.remove(storage, key)) {
          saved = { available: true, record: null };
          restore.hidden = true;
          state.textContent = 'Saved draft deleted. The current form is still here until you leave.';
        } else state.textContent = 'Could not delete browser storage. Use browser site-data controls; current input is unchanged.';
      };
      consent.addEventListener('change', () => consent.checked ? save() : clear());
      discard.addEventListener('click', clear);
      restore.addEventListener('click', () => {
        saved = store.read(storage, key);
        if (!saved.record) { offer(); return; }
        for (const [name, value] of Object.entries(saved.record.fields)) {
          const field = briefForm.elements.namedItem(name);
          if (field && (field.tagName !== 'SELECT' || Array.from(field.options).some((option) => option.value === value))) field.value = value;
        }
        showServicePrompt();
        consent.checked = true;
        if (isWizard) { step = 0; renderStep(); }
        if (!result.hidden) syncBrief();
        restore.hidden = true;
        state.textContent = describe(saved.record, 'Restored draft from');
        briefForm.elements.namedItem('location')?.focus();
      });
      briefForm.addEventListener('input', save);
      briefForm.addEventListener('change', save);
    }

    // Keep draft and handoff links synchronized whenever inputs change.
    briefForm.addEventListener('input', () => {
      if (!result.hidden) syncBrief();
    });
    briefForm.addEventListener('change', () => {
      if (!result.hidden) syncBrief();
    });

    briefForm.addEventListener('submit', (event) => {
      event.preventDefault();
      if (isWizard && step !== steps.length - 1) return;
      syncBrief();
      result.hidden = false;
      status.textContent = contactEmail || contactTel
        ? 'Your draft is ready. Choose a direct handoff, copy it, or use the listing.'
        : 'Your draft is ready. Copy or download it to keep. Business contact details are not available in this preview; nothing has been sent.';

      try { result.focus({ preventScroll: true }); } catch { result.focus(); }
      result.scrollIntoView({ behavior: reducedMotion() ? 'auto' : 'smooth', block: 'nearest' });
    });

    copyButton?.addEventListener('click', async () => {
      syncBrief();
      if (!latestBrief) return;
      try {
        if (!navigator.clipboard || !window.isSecureContext) throw new Error('Clipboard unavailable');
        await navigator.clipboard.writeText(latestBrief);
        status.textContent = 'Copied. Paste the brief into a message or bring it to a call.';
      } catch {
        const selection = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(briefTextElement);
        selection.removeAllRanges();
        selection.addRange(range);
        status.textContent = 'The brief is selected—copy it with your keyboard, then choose a contact option.';
      }
    });

    downloadButton?.addEventListener('click', () => {
      syncBrief();
      const url = URL.createObjectURL(new Blob([latestBrief], { type: 'text/plain;charset=utf-8' }));
      const link = document.createElement('a');
      link.href = url;
      link.download = `${briefForm.dataset.profileId || 'construction'}-project-brief.txt`;
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      status.textContent = `Download requested. Check your downloads for the brief. Downloading does not send it to ${companyName}.`;
    });

  });  });


})();
