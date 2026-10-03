(() => {
  const pairings = {
    editorial: { title: "'Libre Caslon Display', Georgia, serif", body: "'DM Sans', system-ui, sans-serif", label: 'Editorial', number: '01' },
    literary: { title: "'EB Garamond', Georgia, serif", body: "'Source Sans 3', system-ui, sans-serif", label: 'Literary', number: '02' },
    warm: { title: "'Lora', Georgia, serif", body: "'Inter', system-ui, sans-serif", label: 'Warm', number: '03' },
    character: { title: "'Fraunces', Georgia, serif", body: "'DM Sans', system-ui, sans-serif", label: 'Bookshop', number: '04' },
    journal: { title: "'Newsreader', Georgia, serif", body: "'Work Sans', system-ui, sans-serif", label: 'Journal', number: '05' }
  };
  // Keep round-one preferences separate so the chosen Bookshop direction
  // starts with its actual pairing rather than an earlier comparison choice.
  const storageKey = 'well-read-bookshop-font-pairing';
  const picker = document.querySelector('.font-picker');
  const toggle = document.querySelector('#font-picker-toggle');
  const panel = document.querySelector('#font-picker-panel');
  const status = document.querySelector('#font-picker-status');
  const radios = Array.from(picker.querySelectorAll('input[name="font-pairing"]'));

  function applyPairing(key, announce = false) {
    const pairing = pairings[key];
    if (!pairing) return;
    document.documentElement.style.setProperty('--font-title', pairing.title);
    document.documentElement.style.setProperty('--font-body', pairing.body);
    radios.forEach(radio => { radio.checked = radio.value === key; });
    document.querySelector('#font-picker-current').textContent = pairing.number;
    toggle.setAttribute('aria-label', `Try the fonts. Current pairing: ${pairing.label}`);
    if (announce) status.textContent = `${pairing.label} title and body fonts applied.`;
  }

  function setOpen(open, restoreFocus = false) {
    panel.hidden = !open;
    toggle.setAttribute('aria-expanded', String(open));
    if (open) radios.find(radio => radio.checked)?.focus();
    else if (restoreFocus) toggle.focus();
  }

  let saved;
  try { saved = localStorage.getItem(storageKey); } catch { /* Browser may disable storage. */ }
  applyPairing(Object.hasOwn(pairings, saved) ? saved : 'character');
  toggle.addEventListener('click', () => setOpen(panel.hidden));
  document.querySelector('#font-picker-close').addEventListener('click', () => setOpen(false, true));
  picker.addEventListener('change', event => {
    if (!event.target.matches('input[name="font-pairing"]')) return;
    applyPairing(event.target.value, true);
    try { localStorage.setItem(storageKey, event.target.value); } catch { /* Selection still works without persistence. */ }
  });
  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && !panel.hidden) { setOpen(false, picker.contains(document.activeElement)); }
  });
  document.addEventListener('click', event => {
    if (!panel.hidden && !picker.contains(event.target)) setOpen(false);
  });
})();
