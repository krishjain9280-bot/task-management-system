/**
 * auth.js
 * --------
 * Client-side handling for the login and signup forms:
 *  - basic inline validation before hitting the API
 *  - calls POST /api/login or POST /api/signup
 *  - shows field-level errors returned by the server
 *  - redirects to the dashboard on success
 */

function clearErrors(form) {
  form.querySelectorAll(".form-error").forEach((el) => (el.textContent = ""));
}

function setFieldError(name, message) {
  const el = document.getElementById("err-" + name);
  if (el) el.textContent = message;
}

function setLoading(button, textEl, loadingText) {
  button.disabled = true;
  button.dataset.originalText = textEl.textContent;
  textEl.innerHTML = `<span class="spinner"></span> ${loadingText}`;
}

function clearLoading(button, textEl) {
  button.disabled = false;
  textEl.textContent = button.dataset.originalText;
}

// ------------------------------------------------------------- LOGIN ----
const loginForm = document.getElementById("loginForm");
if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearErrors(loginForm);

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;

    let valid = true;
    if (!username) { setFieldError("username", "This field is required."); valid = false; }
    if (!password) { setFieldError("password", "Password is required."); valid = false; }
    if (!valid) return;

    const btn = document.getElementById("loginSubmit");
    const txt = document.getElementById("loginSubmitText");
    setLoading(btn, txt, "Logging in...");

    const result = await apiRequest("/api/login", { method: "POST", body: { username, password } });

    if (result.success) {
      showToast(result.message || "Logged in!", "success");
      setTimeout(() => (window.location.href = "/dashboard"), 350);
    } else {
      clearLoading(btn, txt);
      showToast(result.message || "Login failed.", "error");
    }
  });
}

// ------------------------------------------------------------ SIGNUP ----
const signupForm = document.getElementById("signupForm");
if (signupForm) {
  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearErrors(signupForm);

    const full_name = document.getElementById("full_name").value.trim();
    const username = document.getElementById("username").value.trim();
    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    const confirm_password = document.getElementById("confirm_password").value;

    let valid = true;
    if (full_name.length < 2) { setFieldError("full_name", "Enter your full name."); valid = false; }
    if (!/^[a-zA-Z0-9_.]{3,30}$/.test(username)) { setFieldError("username", "3-30 chars: letters, numbers, _ or ."); valid = false; }
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) { setFieldError("email", "Enter a valid email."); valid = false; }
    if (password.length < 6) { setFieldError("password", "At least 6 characters."); valid = false; }
    if (password !== confirm_password) { setFieldError("confirm_password", "Passwords don't match."); valid = false; }
    if (!valid) return;

    const btn = document.getElementById("signupSubmit");
    const txt = document.getElementById("signupSubmitText");
    setLoading(btn, txt, "Creating account...");

    const result = await apiRequest("/api/signup", {
      method: "POST",
      body: { full_name, username, email, password, confirm_password },
    });

    if (result.success) {
      showToast(result.message || "Account created!", "success");
      setTimeout(() => (window.location.href = "/login"), 500);
    } else {
      clearLoading(btn, txt);
      if (result.errors) {
        Object.entries(result.errors).forEach(([field, msg]) => setFieldError(field, msg));
      }
      showToast(result.message || "Sign up failed.", "error");
    }
  });
}
