// Connect an approved mailing-list integration before enabling email collection.
(() => {
  const form = document.querySelector('#starter-form');
  form.addEventListener('submit', event => {
    event.preventDefault();
    const status = document.querySelector('#signup-status');
    status.textContent = 'Email signup is not connected yet. Your address has not been sent or saved.';
    status.focus();
  });
})();
