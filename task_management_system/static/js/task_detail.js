/**
 * task_detail.js
 * ---------------
 * Powers the Task Details page:
 *  - GET /api/tasks/<task_id> on load, populates the edit form + metadata
 *  - PUT /api/tasks/<task_id> on "Save Changes"
 *  - DELETE /api/tasks/<task_id> via the delete confirmation modal
 */

async function loadTask() {
  const result = await apiRequest(`/api/tasks/${window.TASK_ID}`);

  if (!result.success) {
    showToast(result.message || "Task not found.", "error");
    setTimeout(() => (window.location.href = "/tasks"), 800);
    return;
  }

  const t = result.task;
  document.getElementById("title").value = t.title;
  document.getElementById("description").value = t.description || "";
  document.getElementById("owner_name").value = t.owner_name;
  document.getElementById("status").value = t.status;

  document.getElementById("metaStatus").innerHTML = `<span class="status-badge ${statusClass(t.status)}">${t.status}</span>`;
  document.getElementById("metaOwner").textContent = t.owner_name;
  document.getElementById("metaCreated").textContent = formatDate(t.created_at);
  document.getElementById("metaUpdated").textContent = formatDate(t.updated_at);

  document.getElementById("detailLoading").style.display = "none";
  document.getElementById("detailContent").style.display = "grid";
}

document.getElementById("editTaskForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  document.querySelectorAll(".form-error").forEach((el) => (el.textContent = ""));

  const title = document.getElementById("title").value.trim();
  const description = document.getElementById("description").value.trim();
  const owner_name = document.getElementById("owner_name").value.trim();
  const status = document.getElementById("status").value;

  let valid = true;
  if (title.length < 3) {
    document.getElementById("err-title").textContent = "Title must be at least 3 characters.";
    valid = false;
  }
  if (!owner_name) {
    document.getElementById("err-owner_name").textContent = "Owner is required.";
    valid = false;
  }
  if (!valid) return;

  const btn = document.getElementById("saveBtn");
  const txt = document.getElementById("saveBtnText");
  btn.disabled = true;
  txt.innerHTML = `<span class="spinner"></span> Saving...`;

  const result = await apiRequest(`/api/tasks/${window.TASK_ID}`, {
    method: "PUT",
    body: { title, description, owner_name, status },
  });

  btn.disabled = false;
  txt.textContent = "Save Changes";

  if (result.success) {
    showToast(result.message || "Task updated!", "success");
    loadTask();
  } else {
    if (result.errors) {
      Object.entries(result.errors).forEach(([field, msg]) => {
        const el = document.getElementById("err-" + field);
        if (el) el.textContent = msg;
      });
    }
    showToast(result.message || "Could not update task.", "error");
  }
});

// ---------------------------------------------------------------- DELETE --
document.getElementById("deleteBtn").addEventListener("click", () => {
  document.getElementById("deleteModal").style.display = "flex";
});
document.getElementById("cancelDeleteBtn").addEventListener("click", () => {
  document.getElementById("deleteModal").style.display = "none";
});
document.getElementById("confirmDeleteBtn").addEventListener("click", async () => {
  const btn = document.getElementById("confirmDeleteBtn");
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span> Deleting...`;

  const result = await apiRequest(`/api/tasks/${window.TASK_ID}`, { method: "DELETE" });

  if (result.success) {
    showToast(result.message || "Task deleted.", "success");
    setTimeout(() => (window.location.href = "/tasks"), 400);
  } else {
    btn.disabled = false;
    btn.textContent = "Delete";
    showToast(result.message || "Could not delete task.", "error");
  }
});

document.addEventListener("DOMContentLoaded", loadTask);
