(() => {
  const directions = document.querySelector('#directions');
  const cards = Array.from(document.querySelectorAll('[data-direction]'));
  const viewButtons = Array.from(document.querySelectorAll('[data-view]'));
  const viewportButtons = Array.from(document.querySelectorAll('[data-viewport]'));
  let viewport = 'desktop';
  function fitPreviews() {
    const width = viewport === 'mobile' ? 390 : 1200;
    const height = viewport === 'mobile' ? 1650 : 1500;
    cards.forEach(card => {
      if (card.hidden) return;
      const frame = card.querySelector('iframe');
      const container = card.querySelector('.frame-window');
      const available = container.clientWidth;
      if (!available) return;
      const scale = Math.min(available / width, 1);
      frame.style.width = `${width}px`;
      frame.style.height = `${height}px`;
      frame.style.transform = `scale(${scale})`;
      container.style.height = `${Math.ceil(height * scale)}px`;
    });
  }
  viewButtons.forEach(button => button.addEventListener('click', () => {
    const view = button.dataset.view;
    cards.forEach(card => { card.hidden = view !== 'all' && card.dataset.direction !== view; });
    viewButtons.forEach(control => control.setAttribute('aria-pressed', String(control === button)));
    directions.classList.toggle('focused', view !== 'all');
    document.querySelector('#review-status').textContent = view === 'all' ? 'Comparing all three directions.' : `Previewing ${view}.`;
    fitPreviews();
  }));
  viewportButtons.forEach(button => button.addEventListener('click', () => {
    viewport = button.dataset.viewport;
    viewportButtons.forEach(control => control.setAttribute('aria-pressed', String(control === button)));
    directions.classList.toggle('mobile', viewport === 'mobile');
    document.querySelector('#review-status').textContent = `${viewport} layouts shown.`;
    fitPreviews();
  }));
  const observer = new ResizeObserver(fitPreviews);
  cards.forEach(card => observer.observe(card.querySelector('.frame-window')));
  window.addEventListener('resize', fitPreviews);
  fitPreviews();
})();
