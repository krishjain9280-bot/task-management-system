/**
 * task_create.js
 * ---------------
 * Handles the "New Task" form: validates inputs client-side, submits
 * to POST /api/tasks, and redirects to the new task's detail page on
 * success (so the auto-generated Task ID is immediately visible).
 */

document.addEventListener("DOMContentLoaded", async () => {
  // Pre-fill the owner field with the current user's name for convenience.
  const profileResult = await apiRequest("/api/profile");
  if (profileResult.success) {
    document.getElementById("owner_name").value = profileResult.profile.full_name;
  }
});

document.getElementById("createTaskForm").addEventListener("submit", async (e) => {
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

  const btn = document.getElementById("createSubmit");
  const txt = document.getElementById("createSubmitText");
  btn.disabled = true;
  txt.innerHTML = `<span class="spinner"></span> Creating...`;

  const result = await apiRequest("/api/tasks", {
    method: "POST",
    body: { title, description, owner_name, status },
  });

  if (result.success) {
    showToast(result.message || "Task created!", "success");
    setTimeout(() => (window.location.href = `/tasks/${result.task.task_id}`), 400);
  } else {
    btn.disabled = false;
    txt.textContent = "Create Task";
    if (result.errors) {
      Object.entries(result.errors).forEach(([field, msg]) => {
        const el = document.getElementById("err-" + field);
        if (el) el.textContent = msg;
      });
    }
    showToast(result.message || "Could not create task.", "error");
  }
});
