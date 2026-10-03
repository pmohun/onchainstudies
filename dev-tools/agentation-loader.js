// Annotation tools run only on a local, top-level preview.
if (['localhost', '127.0.0.1', '[::1]'].includes(location.hostname) && window.self === window.top) {
  import('../.local/agentation.js').then(() => {
    document.documentElement.classList.add('annotation-dev');
  }).catch(error => console.warn('Agentation: run npm run build:annotations, then refresh.', error));
}
