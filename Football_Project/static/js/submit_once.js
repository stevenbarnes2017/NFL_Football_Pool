// Forms marked data-submit-once can only be sent once: after the first
// submit the button is disabled and shows "Posting…", so double-clicks and
// impatient re-clicks don't create duplicate posts. The server also ignores
// repeats; this just keeps people from trying.
(function () {
  const RESET_AFTER_MS = 20000; // let them try again if the request never finishes

  function buttonsOf(form) {
    return form.querySelectorAll('button[type="submit"], input[type="submit"], button:not([type])');
  }

  function reset(form) {
    delete form.dataset.submitting;
    buttonsOf(form).forEach((b) => {
      b.disabled = false;
      if (b.dataset.originalText) {
        b.textContent = b.dataset.originalText;
        delete b.dataset.originalText;
      }
    });
  }

  document.addEventListener("submit", (e) => {
    const form = e.target;
    if (!form.matches || !form.matches("form[data-submit-once]")) return;

    if (form.dataset.submitting) {
      e.preventDefault();
      return;
    }

    // Wait a tick: other handlers (e.g. "please write a message first") may
    // cancel the submit, and disabling now would drop the button's value.
    setTimeout(() => {
      if (e.defaultPrevented) return;
      form.dataset.submitting = "1";
      buttonsOf(form).forEach((b) => {
        b.disabled = true;
        if (b.tagName === "BUTTON") {
          b.dataset.originalText = b.textContent;
          b.textContent = "Posting…";
        }
      });
      setTimeout(() => reset(form), RESET_AFTER_MS);
    }, 0);
  });

  // Coming back with the browser's Back button can restore the page as it
  // was left (button disabled); make it usable again.
  window.addEventListener("pageshow", (e) => {
    if (e.persisted) document.querySelectorAll("form[data-submit-once]").forEach(reset);
  });
})();
