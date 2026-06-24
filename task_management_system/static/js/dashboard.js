/**
 * dashboard.js
 * -------------
 * Loads dashboard stats (total/open/in-progress/completed counts) and
 * a "recently created" tasks table from GET /api/dashboard/stats.
 */

async function loadDashboard() {
  const result = await apiRequest("/api/dashboard/stats");
  if (!result.success) {
    showToast(result.message || "Could not load dashboard.", "error");
    return;
  }

  document.getElementById("statTotal").textContent = result.stats.total;
  document.getElementById("statOpen").textContent = result.stats.open;
  document.getElementById("statProgress").textContent = result.stats.in_progress;
  document.getElementById("statCompleted").textContent = result.stats.completed;

  const tbody = document.getElementById("recentTableBody");
  if (!result.recent_tasks.length) {
    tbody.innerHTML = `<tr><td colspan="5">
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
        <h4>No tasks yet</h4>
        <p>Create your first task to see it here.</p>
      </div></td></tr>`;
    return;
  }

  tbody.innerHTML = result.recent_tasks.map((t) => `
    <tr onclick="window.location.href='/tasks/${t.task_id}'">
      <td><span class="task-id-badge">${t.task_id}</span></td>
      <td class="task-title-cell">${escapeHtml(t.title)}</td>
      <td>${escapeHtml(t.owner_name)}</td>
      <td><span class="status-badge ${statusClass(t.status)}">${t.status}</span></td>
      <td>${formatDate(t.created_at)}</td>
    </tr>
  `).join("");
}

document.addEventListener("DOMContentLoaded", loadDashboard);
