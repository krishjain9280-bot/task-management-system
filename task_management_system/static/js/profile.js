/**
 * profile.js
 * -----------
 * Powers the Profile page:
 *  - tab switching (Account Info / Change Password / Activity Log)
 *  - loads GET /api/profile and fills the form + avatar initials
 *  - PUT /api/profile to save name/email
 *  - PUT /api/profile/password to change password
 *  - GET /api/activity-log to render the activity feed
 */

// --------------------------------------------------------------- TABS ----
document.querySelectorAll(".profile-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".profile-tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach((p) => (p.style.display = "none"));
    tab.classList.add("active");
    document.getElementById("tab-" + tab.dataset.tab).style.display = "block";
    if (tab.dataset.tab === "activity") loadActivity();
  });
});

// ------------------------------------------------------------- LOAD ------
function initials(name) {
  return (name || "").trim().split(/\s+/).map((w) => w[0]).slice(0, 2).join("").toUpperCase();
}

async function loadProfile() {
  const result = await apiRequest("/api/profile");
  if (!result.success) {
    showToast(result.message || "Could not load profile.", "error");
    return;
  }
  const p = result.profile;
  document.getElementById("profileAvatar").textContent = initials(p.full_name) || "?";
  document.getElementById("profileFullName").textContent = p.full_name;
  document.getElementById("profileUsername").textContent = "@" + p.username;
  document.getElementById("usernameField").value = p.username;
  document.getElementById("full_name").value = p.full_name;
  document.getElementById("email").value = p.email;
  document.getElementById("ownedTotal").textContent = p.owned_tasks;
  document.getElementById("ownedCompleted").textContent = p.owned_completed;
}

// ----------------------------------------------------------- SAVE INFO ---
document.getElementById("profileForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.querySelectorAll("#tab-info .form-error").forEach((el) => (el.textContent = ""));

  const full_name = document.getElementById("full_name").value.trim();
  const email = document.getElementById("email").value.trim();

  const btn = document.getElementById("profileSaveBtn");
  const txt = document.getElementById("profileSaveBtnText");
  btn.disabled = true;
  txt.innerHTML = `<span class="spinner"></span> Saving...`;

  const result = await apiRequest("/api/profile", { method: "PUT", body: { full_name, email } });

  btn.disabled = false;
  txt.textContent = "Save Changes";

  if (result.success) {
    showToast(result.message || "Profile updated!", "success");
    loadProfile();
  } else {
    if (result.errors) {
      Object.entries(result.errors).forEach(([field, msg]) => {
        const el = document.getElementById("err-" + field);
        if (el) el.textContent = msg;
      });
    }
    showToast(result.message || "Could not update profile.", "error");
  }
});

// ----------------------------------------------------------- PASSWORD ----
document.getElementById("passwordForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.querySelectorAll("#tab-password .form-error").forEach((el) => (el.textContent = ""));

  const current_password = document.getElementById("current_password").value;
  const new_password = document.getElementById("new_password").value;
  const confirm_new_password = document.getElementById("confirm_new_password").value;

  let valid = true;
  if (!current_password) { document.getElementById("err-current_password").textContent = "Required."; valid = false; }
  if (new_password.length < 6) { document.getElementById("err-new_password").textContent = "At least 6 characters."; valid = false; }
  if (new_password !== confirm_new_password) { document.getElementById("err-confirm_new_password").textContent = "Passwords don't match."; valid = false; }
  if (!valid) return;

  const btn = document.getElementById("passwordSaveBtn");
  const txt = document.getElementById("passwordSaveBtnText");
  btn.disabled = true;
  txt.innerHTML = `<span class="spinner"></span> Updating...`;

  const result = await apiRequest("/api/profile/password", {
    method: "PUT",
    body: { current_password, new_password, confirm_password: confirm_new_password },
  });

  btn.disabled = false;
  txt.textContent = "Update Password";

  if (result.success) {
    showToast(result.message || "Password updated!", "success");
    document.getElementById("passwordForm").reset();
  } else {
    showToast(result.message || "Could not update password.", "error");
  }
});

// ------------------------------------------------------------ ACTIVITY ---
const actionLabels = {
  LOGIN: "logged in",
  LOGOUT: "logged out",
  ACCOUNT_CREATED: "created their account",
  TASK_CREATED: "created a task",
  TASK_UPDATED: "updated a task",
  TASK_DELETED: "deleted a task",
  PROFILE_UPDATED: "updated their profile",
  PASSWORD_CHANGED: "changed their password",
};

async function loadActivity() {
  const list = document.getElementById("activityList");
  const result = await apiRequest("/api/activity-log?limit=30");
  if (!result.success) {
    list.innerHTML = `<p style="color:var(--text-soft)">Could not load activity.</p>`;
    return;
  }
  if (!result.logs.length) {
    list.innerHTML = `<div class="empty-state"><h4>No activity yet</h4><p>Actions you take will show up here.</p></div>`;
    return;
  }
  list.innerHTML = result.logs.map((log) => `
    <div class="activity-item">
      <span class="activity-dot"></span>
      <div>
        <div class="activity-text"><strong>${escapeHtml(log.username)}</strong> ${actionLabels[log.action] || log.action.toLowerCase()}${log.details ? " — " + escapeHtml(log.details) : ""}</div>
        <div class="activity-time">${timeAgo(log.timestamp)}</div>
      </div>
    </div>
  `).join("");
}

document.addEventListener("DOMContentLoaded", loadProfile);
