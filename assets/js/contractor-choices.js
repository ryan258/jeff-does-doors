/* Independent, repeatable radio-to-panel choices. No storage or network calls.
   Without JS, controls stay hidden and every option's content is readable. */
(() => {
  'use strict';
  document.querySelectorAll('[data-contractor-choice]').forEach((root) => {
    if (root.dataset.choiceReady === 'true') return;
    const controls = root.querySelector('[data-choice-controls]');
    const status = root.querySelector('[data-choice-status]');
    const inputs = Array.from(root.querySelectorAll('[data-choice-input]'));
    const panels = Array.from(root.querySelectorAll('[data-choice-panel]'));
    const values = inputs.map((input) => input.value);
    const panelValues = panels.map((panel) => panel.dataset.choicePanel);
    // Validate the whole local mapping before hiding any fallback content.
    if (!controls || !status || !inputs.length || inputs.length !== panels.length
      || new Set(values).size !== values.length
      || new Set(panelValues).size !== panelValues.length
      || values.some((value) => !panelValues.includes(value))) return;

    const showChoice = (input, announce) => {
      panels.forEach((panel) => { panel.hidden = panel.dataset.choicePanel !== input.value; });
      if (announce) status.textContent = `Showing ${input.dataset.choiceLabel}.`;
    };
    inputs.forEach((input) => {
      input.addEventListener('change', () => {
        if (input.checked) showChoice(input, true);
      });
    });
    const initial = inputs.find((input) => input.checked) || inputs[0];
    initial.checked = true;
    showChoice(initial, false);
    controls.hidden = false;
    root.dataset.choiceReady = 'true';
  });
})();
