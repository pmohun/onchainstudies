// Keep empty until starter-box pricing/terms are approved AND secure profile capture, verified
// payment handling, and digital starter-shelf delivery are implemented.
// Only use a Stripe-hosted HTTPS Payment Link here; never put a secret key in this file.
const STARTER_BOX_PAYMENT_LINK = '';
const dialog = document.querySelector('#checkout-dialog');
const openButton = document.querySelector('#open-checkout');
const form = document.querySelector('#checkout-form');
openButton.addEventListener('click', () => {
  if (STARTER_BOX_PAYMENT_LINK) {
    const link = new URL(STARTER_BOX_PAYMENT_LINK);
    if (link.protocol === 'https:' && link.hostname === 'buy.stripe.com') {
      window.location.assign(link.href);
      return;
    }
  }
  dialog.showModal();
});
document.querySelector('#close-checkout').addEventListener('click', () => dialog.close());
dialog.addEventListener('click', (event) => {
  if (event.target === dialog) {
    const bounds = dialog.getBoundingClientRect();
    if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
  }
});
form.addEventListener('submit', (event) => {
  event.preventDefault();
  const status = document.querySelector('#checkout-status');
  status.textContent = 'The live flow will collect a shipping address, show the final one-time total, and take payment before delivering your digital starter shelf. This preview sent no information, charged nothing, and reserved no box.';
  status.focus();
});
dialog.addEventListener('close', () => {
  form.reset();
  document.querySelector('#checkout-status').textContent = '';
});
