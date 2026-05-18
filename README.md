# 📄 Document Generation API

A FastAPI backend for managing training course data and generating official Word documents from `.docx` templates. The system handles master data, training batches, applicants, and loan records — and produces ready-to-download Word or ZIP document packages.

---

## 🏗️ Architecture

The project follows an **MVC-style** structure:

| Layer | Folder | Responsibility |
|---|---|---|
| Model | `app/models/` | Request schemas and data validation |
| Controller | `app/controllers/` | API endpoints and business logic |
| View | `app/views/templates/` | Word document templates |
| Config | `app/config/` | Database connection and shared settings |

---

## ✨ Features

- 🔐 **Authentication** — Session-based login with HTTP-only cookie
- 👤 **User Management** — Admin CRUD for system users
- 📋 **Training Batch Management** — Full CRUD with batch detail lookup
- 👥 **Applicant Management** — Bulk create, bulk result update, batch-based lookup
- 🗂️ **Master Data** — Courses, instructors, locations, and staff management
- 📁 **Project Management** — Activities, master plans, and master projects
- 📅 **Calendar Events** — CRUD with automatic expired-event cleanup on startup
- 💰 **Loan Records** — Update clearance, lookup, and delete by batch
- 📝 **Template Management** — Admin upload, download, and listing of `.docx` templates
- 📄 **Document Generation** — Generate individual Word documents from templates
- 📦 **ZIP Export** — Bundle all related training documents in a single request

---

## 🛠️ Tech Stack

| Tool | Version | Purpose |
|---|---|---|
| Python | 3.x | Backend runtime |
| FastAPI | 0.121.3 | API framework |
| Uvicorn | 0.38.0 | ASGI server |
| MySQL | — | Primary database |

---

## ⚙️ Setup

### 1. Create and activate a virtual environment

```powershell
# Create
py -m venv venv

# Activate (Windows)
.\venv\Scripts\Activate.ps1
```

> If `py` is not available, use `python` instead.

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=training_db
```

### 4. Set up the database

Make sure MySQL is running, then create the database:

```sql
CREATE DATABASE training_db;
```

### 5. Add document templates

Place all `.docx` template files in:

```
app/views/templates/
```

---

## ▶️ Running the Server

```powershell
uvicorn main:app --reload
```

| | URL |
|---|---|
| Base URL | `http://127.0.0.1:8000` |
| Health Check | `GET /` |
| Interactive Docs | `http://127.0.0.1:8000/docs` |
| API Prefix | `/api/v1` |

---

## 🌐 API Routes

### Authentication
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/auth/login` | Login and set session cookie |

### Admin — Users
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/admin/users` | List all users |
| `POST` | `/api/v1/admin/users` | Create a user |
| `PUT` | `/api/v1/admin/users/{user_id}` | Update a user |
| `DELETE` | `/api/v1/admin/users/{user_id}` | Delete a user |

### Admin — Templates
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/admin/templates` | List available templates |
| `GET` | `/api/v1/admin/templates/{filename}/download` | Download a template |
| `POST` | `/api/v1/admin/templates/{filename}/upload` | Upload and replace a template |

### Training Batches
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/training_batches` | Create a batch |
| `GET` | `/api/v1/training_batches` | List all batches |
| `GET` | `/api/v1/training_batches/detail/{batch_code}` | Get batch detail |
| `PUT` | `/api/v1/training_batches/{id}` | Update a batch |
| `DELETE` | `/api/v1/training_batches/{id}` | Delete a batch |

### Applicants
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/applicants/bulk` | Bulk create applicants |
| `GET` | `/api/v1/applicants` | List all applicants |
| `GET` | `/api/v1/applicants/{id}` | Get applicant by ID |
| `PUT` | `/api/v1/applicants/bulk-update-result` | Bulk update results |
| `PUT` | `/api/v1/applicants/{id}` | Update an applicant |
| `GET` | `/api/v1/applicants/batch/{batch_code}` | List applicants by batch |
| `DELETE` | `/api/v1/applicants/{id}` | Delete an applicant |

### Master Data — Courses
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/master_courses` | Create a course |
| `GET` | `/api/v1/master_courses` | List all courses |
| `GET` | `/api/v1/master_courses/{id}` | Get course by ID |
| `PUT` | `/api/v1/master_courses/{id}` | Update a course |
| `DELETE` | `/api/v1/master_courses/{id}` | Delete a course |

### Master Data — Instructors, Locations, Staff

> All three follow the same CRUD pattern as Courses above.

| Resource | Base Path |
|---|---|
| Instructors | `/api/v1/instructors` |
| Locations | `/api/v1/locations` |
| Staff | `/api/v1/staff` |

### Project Management
| Method | Path | Description |
|---|---|---|
| `POST/GET/PUT/DELETE` | `/api/v1/project_activities/{id?}` | Project activities CRUD |
| `POST/GET/PUT/DELETE` | `/api/v1/master_plans/{id?}` | Master plans CRUD |
| `POST/GET/PUT/DELETE` | `/api/v1/master_projects/{id?}` | Master projects CRUD |

### Calendar Events
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/events` | List all events |
| `GET` | `/api/v1/events/{id}` | Get event by ID |
| `POST` | `/api/v1/events` | Create an event |
| `PUT` | `/api/v1/events/{id}` | Update an event |
| `DELETE` | `/api/v1/events/{id}` | Delete an event |
| `DELETE` | `/api/v1/events-cleanup` | Remove all expired events |

### Loan Records
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/v1/loan/update-clearance` | Update loan clearance |
| `GET` | `/api/v1/loans` | List all loans |
| `GET` | `/api/v1/loan/batch/{batch_code}` | Get loans by batch |
| `DELETE` | `/api/v1/loan/batch/{batch_code}` | Delete loans by batch |

### Document Generation
| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/generate-doc/{batch_code}` | Approval training document |
| `GET` | `/api/v1/generate-schedule/{batch_code}` | Applicant schedule document |
| `GET` | `/api/v1/Material/{batch_code}` | Material document |
| `GET` | `/api/v1/generate-food/{batch_code}` | Food loan document |
| `GET` | `/api/v1/generate-food-snack/{batch_code}` | Snack loan document |
| `GET` | `/api/v1/generate-inst/{batch_code}` | Instructor loan document |
| `GET` | `/api/v1/complete/{batch_code}` | Completion announcement |
| `GET` | `/api/v1/summary/{batch_code}` | Loan summary document |
| `GET` | `/api/v1/generate-all/{batch_code}` | **All documents as ZIP** |

---

## 🗂️ Folder Structure

```
Myproject/
├── app/
│   ├── config/
│   │   ├── database.py
│   │   └── settings.py
│   ├── controllers/
│   │   ├── auth_router.py
│   │   ├── admin_router.py
│   │   ├── batch_router.py
│   │   ├── applicants.py
│   │   ├── courses.py
│   │   ├── instructors.py
│   │   ├── locations.py
│   │   ├── staff.py
│   │   ├── loan_router.py
│   │   ├── calender_router.py
│   │   ├── activity_router.py
│   │   ├── template_router.py
│   │   └── ... (document generation controllers)
│   ├── models/
│   │   ├── auth_model.py
│   │   ├── batch_model.py
│   │   ├── applicant_model.py
│   │   └── ... (other models)
│   └── views/
│       └── templates/
│           ├── Template.docx
│           ├── applicant.docx
│           ├── announce_date.docx
│           ├── food_borrow.docx
│           ├── food_snack_borrow.docx
│           ├── inst_borrow.docx
│           ├── material.docx
│           └── refund_summary.docx
├── main.py
├── requirements.txt
├── reset_password.py
├── .env
└── .gitignore
```

---

## 🔧 Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `DB_HOST` | No | `localhost` | MySQL host address |
| `DB_USER` | No | `root` | MySQL username |
| `DB_PASSWORD` | No | *(empty)* | MySQL password |
| `DB_NAME` | No | `training_db` | Database name |

> Variables are loaded from `.env` via `app/config/database.py`.

---

## 📝 Notes

- **Startup cleanup** — Expired calendar events are automatically deleted when the server starts.
- **CORS** — Currently configured for `http://127.0.0.1:5500`.
- **Document output** — Generated files are returned as direct downloads.
- **Template storage** — All `.docx` templates are read from `app/views/templates/`.
- **Admin routes** — Template upload/download requires a valid admin session cookie.
