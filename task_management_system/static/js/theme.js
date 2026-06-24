/**
 * theme.js
 * ---------
 * Handles dark/light mode toggling. The preference is persisted in
 * localStorage so it survives page reloads and new tabs/sessions on
 * the same browser - this is a real multi-page app (not a sandboxed
 * single-page artifact), so localStorage is the correct, standard tool.
 */
(function () {
  const STORAGE_KEY = "taskflow-theme";
  const root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    const label = document.querySelector(".theme-label");
    if (label) label.textContent = theme === "dark" ? "Light mode" : "Dark mode";
  }

  // Apply saved theme immediately (before paint where possible)
  const saved = localStorage.getItem(STORAGE_KEY) ||
    (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  applyTheme(saved);

  document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("themeToggle");
    if (!toggle) return;
    toggle.addEventListener("click", function () {
      const current = root.getAttribute("data-theme");
      const next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem(STORAGE_KEY, next);
    });
  });
})();
