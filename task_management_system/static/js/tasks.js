/**
 * tasks.js
 * ---------
 * Powers the Tasks list page:
 *  - debounced search box
 *  - status filter chips
 *  - paginated table rendering
 *  - delete confirmation modal wired to DELETE /api/tasks/<id>
 */

let state = { q: "", status: "", page: 1, per_page: 8, pendingDeleteId: null };
let debounceTimer = null;

async function loadTasks() {
  const tbody = document.getElementById("tasksTableBody");
  tbody.innerHTML = `<tr><td colspan="6"><div class="loading-row"><span class="spinner"></span> Loading tasks…</div></td></tr>`;

  const params = new URLSearchParams({
    q: state.q, status: state.status, page: state.page, per_page: state.per_page,
  });
  const result = await apiRequest(`/api/tasks?${params.toString()}`);

  if (!result.success) {
    showToast(result.message || "Could not load tasks.", "error");
    tbody.innerHTML = `<tr><td colspan="6">Failed to load tasks.</td></tr>`;
    return;
  }

  renderTable(result.tasks);
  renderPagination(result.pagination);
}

function renderTable(tasks) {
  const tbody = document.getElementById("tasksTableBody");
  if (!tasks.length) {
    tbody.innerHTML = `<tr><td colspan="6">
      <div class="empty-state">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>
        <h4>No tasks found</h4>
        <p>Try adjusting your search or filters, or create a new task.</p>
      </div></td></tr>`;
    return;
  }

  tbody.innerHTML = tasks.map((t) => `
    <tr onclick="window.location.href='/tasks/${t.task_id}'">
      <td><span class="task-id-badge">${t.task_id}</span></td>
      <td>
        <div class="task-title-cell">${escapeHtml(t.title)}</div>
        ${t.description ? `<div class="task-desc-snippet">${escapeHtml(t.description)}</div>` : ""}
      </td>
      <td>${escapeHtml(t.owner_name)}</td>
      <td><span class="status-badge ${statusClass(t.status)}">${t.status}</span></td>
      <td>${formatDate(t.updated_at)}</td>
      <td class="row-actions" onclick="event.stopPropagation()">
        <button title="Edit" onclick="window.location.href='/tasks/${t.task_id}'">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.1 2.1 0 0 1 3 3L7 19l-4 1 1-4 12.5-12.5z"/></svg>
        </button>
        <button title="Delete" onclick="openDeleteModal('${t.task_id}', '${escapeHtml(t.title)}')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 6h18"/><path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2m2 0-1 14a2 2 0 0 1-2 2H9a2 2 0 0 1-2-2L6 6"/></svg>
        </button>
      </td>
    </tr>
  `).join("");
}

function renderPagination(p) {
  const el = document.getElementById("pagination");
  if (p.total_pages <= 1) { el.innerHTML = ""; return; }

  let html = `<span class="pagination-info">${p.total} task${p.total !== 1 ? "s" : ""}</span>`;
  html += `<button ${p.page <= 1 ? "disabled" : ""} onclick="goToPage(${p.page - 1})">‹</button>`;

  for (let i = 1; i <= p.total_pages; i++) {
    if (i === 1 || i === p.total_pages || Math.abs(i - p.page) <= 1) {
      html += `<button class="${i === p.page ? "active" : ""}" onclick="goToPage(${i})">${i}</button>`;
    } else if (Math.abs(i - p.page) === 2) {
      html += `<span style="color:var(--text-faint)">…</span>`;
    }
  }
  html += `<button ${p.page >= p.total_pages ? "disabled" : ""} onclick="goToPage(${p.page + 1})">›</button>`;
  el.innerHTML = html;
}

function goToPage(page) {
  state.page = page;
  loadTasks();
}

// --------------------------------------------------------------- SEARCH --
document.getElementById("searchInput").addEventListener("input", (e) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    state.q = e.target.value.trim();
    state.page = 1;
    loadTasks();
  }, 350);
});

// --------------------------------------------------------------- FILTERS --
document.querySelectorAll("#statusFilters .chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    document.querySelectorAll("#statusFilters .chip").forEach((c) => c.classList.remove("active"));
    chip.classList.add("active");
    state.status = chip.dataset.status;
    state.page = 1;
    loadTasks();
  });
});

// ---------------------------------------------------------------- DELETE --
function openDeleteModal(taskId, title) {
  state.pendingDeleteId = taskId;
  document.getElementById("deleteTaskLabel").textContent = `${taskId} — ${title}`;
  document.getElementById("deleteModal").style.display = "flex";
}
function closeDeleteModal() {
  document.getElementById("deleteModal").style.display = "none";
  state.pendingDeleteId = null;
}
document.getElementById("cancelDeleteBtn").addEventListener("click", closeDeleteModal);
document.getElementById("confirmDeleteBtn").addEventListener("click", async () => {
  if (!state.pendingDeleteId) return;
  const btn = document.getElementById("confirmDeleteBtn");
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span> Deleting...`;

  const result = await apiRequest(`/api/tasks/${state.pendingDeleteId}`, { method: "DELETE" });
  btn.disabled = false;
  btn.textContent = "Delete";

  if (result.success) {
    showToast(result.message || "Task deleted.", "success");
    closeDeleteModal();
    loadTasks();
  } else {
    showToast(result.message || "Could not delete task.", "error");
  }
});

document.addEventListener("DOMContentLoaded", loadTasks);
