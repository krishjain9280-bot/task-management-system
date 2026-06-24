/**
 * common.js
 * ----------
 * Shared utilities used by every page:
 *  - showToast()      success / error / info notifications
 *  - apiRequest()      fetch() wrapper that adds JSON headers + error handling
 *  - sidebar toggle for mobile
 *  - logout button wiring
 *  - small formatting helpers (dates, status class names)
 */

// ---------------------------------------------------------------- TOASTS --
function showToast(message, type = "info") {
  const host = document.getElementById("toastHost");
  if (!host) return;

  const icons = {
    success: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M8 12l3 3 5-6"/></svg>',
    error: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v5M12 16h.01"/></svg>',
    info: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-5M12 8h.01"/></svg>',
  };

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `${icons[type] || icons.info}<span>${escapeHtml(message)}</span>`;
  host.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(8px)";
    toast.style.transition = "all .2s ease";
    setTimeout(() => toast.remove(), 220);
  }, 3600);
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

// ------------------------------------------------------------ API CALLS --
async function apiRequest(url, options = {}) {
  const opts = {
    method: options.method || "GET",
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    credentials: "same-origin",
  };
  if (options.body) opts.body = JSON.stringify(options.body);

  try {
    const res = await fetch(url, opts);
    const data = await res.json().catch(() => ({}));

    if (res.status === 401) {
      // Session expired / not logged in - send back to login
      window.location.href = "/login";
      return { success: false, message: "Session expired." };
    }
    return { ...data, _status: res.status };
  } catch (err) {
    return { success: false, message: "Network error. Please check your connection.", _status: 0 };
  }
}

// ------------------------------------------------------------- SIDEBAR ---
document.addEventListener("DOMContentLoaded", () => {
  const hamburger = document.getElementById("hamburger");
  const sidebar = document.getElementById("sidebar");
  if (hamburger && sidebar) {
    hamburger.addEventListener("click", () => sidebar.classList.toggle("open"));
    document.addEventListener("click", (e) => {
      if (window.innerWidth <= 760 && sidebar.classList.contains("open") &&
          !sidebar.contains(e.target) && !hamburger.contains(e.target)) {
        sidebar.classList.remove("open");
      }
    });
  }

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      const result = await apiRequest("/api/logout", { method: "POST" });
      if (result.success) {
        window.location.href = "/login";
      } else {
        showToast(result.message || "Could not log out.", "error");
      }
    });
  }
});

// ------------------------------------------------------------- HELPERS ---
function statusClass(status) {
  return "status-" + (status || "").replace(/\s+/g, "-");
}

function formatDate(isoStr) {
  if (!isoStr) return "-";
  const d = new Date(isoStr.replace(" ", "T"));
  if (isNaN(d)) return isoStr;
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) +
    " " + d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
}

function timeAgo(isoStr) {
  if (!isoStr) return "";
  const d = new Date(isoStr.replace(" ", "T"));
  const diff = Math.floor((Date.now() - d.getTime()) / 1000);
  if (diff < 60) return "just now";
  if (diff < 3600) return Math.floor(diff / 60) + "m ago";
  if (diff < 86400) return Math.floor(diff / 3600) + "h ago";
  return Math.floor(diff / 86400) + "d ago";
}
