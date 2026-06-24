# TaskFlow — Full-Stack Task Management System

A complete, production-ready task management web application.

- **Frontend:** HTML, CSS, vanilla JavaScript (responsive, dark mode, no build step)
- **Backend:** Python Flask (Blueprints, session auth, REST JSON APIs)
- **Database:** SQLite (auto-created on first run, zero external setup)

---

## ✨ Features

- **Authentication** — Signup, Login, Logout, hashed passwords (Werkzeug PBKDF2), server-side sessions
- **Dashboard** — Total / Open / In Progress / Completed counts + recent tasks table
- **Task management** — Create, view, search, filter, edit, delete; auto-generated IDs (`TA1001`, `TA1002`, …)
- **Task detail page** — Dedicated page per task; edit every field and save
- **Profile page** — Update name/email, change password, personal stats
- **Activity log** — Tracks logins, task changes, profile/password updates
- **Dark mode** — Persisted per-browser, toggle in the sidebar
- **Modern UI** — Sidebar navigation, mobile-responsive, status badges, paginated tables, toast notifications, loading skeletons/spinners, client + server-side form validation

---

## 📁 Project Structure

```
task_management_system/
├── app.py                     # Flask app factory & entry point (python app.py)
├── config.py                  # Configuration (secret key, DB path, pagination defaults)
├── database.py                # SQLite connection handling + auto schema creation
├── schema.sql                 # Table definitions (users, tasks, activity_log)
├── requirements.txt           # Python dependencies
├── .gitignore
│
├── routes/                    # Flask Blueprints
│   ├── page_routes.py          # Serves HTML pages (/, /login, /dashboard, /tasks, ...)
│   ├── auth_routes.py          # POST /api/signup, /api/login, /api/logout
│   ├── task_routes.py          # Full task CRUD REST API + dashboard stats + activity log
│   └── profile_routes.py       # GET/PUT /api/profile, PUT /api/profile/password
│
├── utils/
│   ├── decorators.py            # @login_required (pages) / @api_login_required (APIs)
│   └── helpers.py                # generate_task_id(), log_activity(), validators
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html                 # Shared shell: sidebar, topbar, toast host
│   ├── login.html / signup.html  # Standalone auth pages
│   ├── dashboard.html            # Stat cards + recent tasks
│   ├── tasks.html                # Search / filter / paginated task table
│   ├── task_create.html          # New task form
│   ├── task_detail.html          # View & edit one task
│   └── profile.html              # Account info / password / activity tabs
│
├── static/
│   ├── css/style.css             # Full design system (light + dark themes)
│   └── js/
│       ├── theme.js                # Dark mode toggle (localStorage)
│       ├── common.js               # Toasts, fetch wrapper, sidebar, logout, formatters
│       ├── auth.js                 # Login / signup form logic
│       ├── dashboard.js            # Loads dashboard stats + recent tasks
│       ├── tasks.js                # Search, filters, pagination, delete modal
│       ├── task_create.js          # New task form submission
│       ├── task_detail.js          # Load / edit / save / delete a task
│       └── profile.js              # Profile info, password change, activity feed
│
└── instance/                   # Created automatically — holds taskmanager.db (SQLite)
```

---

## 🗄️ Database Schema (`schema.sql`)

| Table           | Purpose                                                                 |
|-----------------|--------------------------------------------------------------------------|
| `users`         | id, username (unique), email (unique), full_name, password_hash, created_at |
| `tasks`         | id, **task_id** (e.g. `TA1001`, unique), title, description, status, owner_id → users.id, owner_name, created_by → users.id, created_at, updated_at |
| `activity_log`  | id, user_id → users.id, action, details, timestamp                      |

Relationships: `tasks.owner_id` and `tasks.created_by` are foreign keys into `users.id` (`ON DELETE CASCADE`). `activity_log.user_id` is a foreign key into `users.id`. Tables are created automatically by `database.py` the first time the app runs — **no manual migration step needed**.

---

## 🔌 REST API Reference

All `/api/*` routes (except signup/login) require an active session and return JSON.

| Method | Endpoint                  | Description                                  |
|--------|----------------------------|-----------------------------------------------|
| POST   | `/api/signup`               | Create a new user account                     |
| POST   | `/api/login`                | Authenticate, start session                    |
| POST   | `/api/logout`               | End session                                    |
| GET    | `/api/tasks`                | List tasks — query params: `q`, `status`, `page`, `per_page` |
| GET    | `/api/tasks/<task_id>`      | Get one task's full details                    |
| POST   | `/api/tasks`                | Create a task (auto-generates Task ID)         |
| PUT    | `/api/tasks/<task_id>`      | Update a task                                  |
| DELETE | `/api/tasks/<task_id>`      | Delete a task                                  |
| GET    | `/api/dashboard/stats`      | Total / open / in-progress / completed counts  |
| GET    | `/api/activity-log`         | Recent activity feed (`?limit=20`)             |
| GET    | `/api/profile`              | Current user's profile + task stats            |
| PUT    | `/api/profile`              | Update full name / email                       |
| PUT    | `/api/profile/password`     | Change password                                |

**Example — create a task:**
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  --cookie "session=<your-session-cookie>" \
  -d '{"title":"Set up CI pipeline","description":"Use GitHub Actions","owner_name":"Jane Doe","status":"Open"}'
```

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+ installed (`python3 --version`)

### 2. Get the code
Unzip the project, then open a terminal in the `task_management_system` folder.

### 3. Create a virtual environment (recommended)
```bash
python3 -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. (Optional) Set a production secret key
```bash
# macOS / Linux
export SECRET_KEY="replace-with-a-long-random-string"

# Windows (PowerShell)
$env:SECRET_KEY="replace-with-a-long-random-string"
```
If skipped, a development default is used — fine for local testing, **not for production**.

### 6. Run the app
```bash
python app.py
```
You should see:
```
* Running on http://0.0.0.0:5000
```
The SQLite database (`instance/taskmanager.db`) and all tables are created automatically the first time this runs.

### 7. Open it in your browser
Go to **http://localhost:5000** → you'll be redirected to the login page.
Click **Sign up** to create your first account, then log in.

---

## 🧪 Quick Manual Test Checklist

1. Sign up with a new account → redirected to login → log in successfully.
2. Dashboard shows all counts at `0`.
3. Click **New Task**, fill the form, submit → redirected to the task's detail page with an ID like `TA1001`.
4. Go to **Tasks**, confirm the task appears; try the search box and status filter chips.
5. Click a row → edit a field → **Save Changes** → see the success toast.
6. Delete a task from the list (trash icon) or from its detail page → confirm in the modal.
7. Go to **Profile** → update your name/email, change your password, check the **Activity Log** tab.
8. Toggle **Dark mode** in the sidebar — preference persists on reload.
9. Resize the browser / open on mobile — sidebar collapses behind the hamburger menu.
10. Click **Log out** → redirected to login; try visiting `/dashboard` directly → redirected back to login.

---

## 🔒 Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` (PBKDF2-SHA256) — never stored or logged in plain text.
- All SQL queries use parameterized statements (no string-concatenated SQL), preventing SQL injection.
- Sessions are server-side (Flask's signed cookie session) and cleared on logout.
- All task/profile API routes are protected by `@api_login_required` and return `401 Unauthorized` JSON if the session is missing or expired.
- For real production deployment: set a strong `SECRET_KEY` via environment variable, run behind HTTPS, and use a production WSGI server (e.g. `gunicorn app:app`) instead of Flask's dev server.

---

## 🛠️ Tech Stack Summary

| Layer        | Technology                                  |
|--------------|----------------------------------------------|
| Frontend     | HTML5, CSS3 (custom design system, CSS variables), vanilla JavaScript (Fetch API) |
| Backend      | Python 3, Flask 3 (Blueprints, sessions)     |
| Database     | SQLite 3 (via Python's built-in `sqlite3`)    |
| Auth         | Werkzeug password hashing + Flask sessions    |
| Fonts        | Sora (headings), Inter (body), JetBrains Mono (Task IDs) |

Enjoy! Feel free to extend this further — e.g. add task comments, due dates, file attachments, or role-based permissions (admin vs. member).
