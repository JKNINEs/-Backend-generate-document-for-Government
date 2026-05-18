# Document Generation API

## Project Summary

Document Generation API is a FastAPI backend for managing training course data and generating official Word documents from `.docx` templates. The project follows an MVC-style structure:

- Models define request and validation schemas.
- Controllers define API endpoints and business workflows.
- Views store document templates used for Word generation.
- Config stores database and shared path settings.

The system connects to a MySQL database, manages master data such as courses, instructors, locations, staff, applicants, training batches, loan records, calendar events, users, and project activities, then generates Word or ZIP document outputs from template files.

## Features

- User login with session token stored in an HTTP-only cookie.
- Admin user management.
- Training batch CRUD and training batch detail lookup.
- Applicant bulk creation, result update, batch lookup, and CRUD.
- Master data management for courses, instructors, locations, and staff.
- Project activity, master plan, and master project management.
- Calendar event CRUD and startup cleanup for expired events.
- Loan record update, lookup, and deletion by training batch.
- Template management for admin users, including list, download, and upload.
- Word document generation from `.docx` templates.
- ZIP generation for all related training documents in one request.
- MVC-style folder organization.

## Tech Tools

| Tool | Version | Purpose |
| --- | --- | --- |
| Python | 3.x | Backend runtime |
| FastAPI | 0.121.3 | API framework |
| Uvicorn | 0.38.0 | ASGI server for running FastAPI |
| MySQL | External database | Stores training, user, applicant, loan, and master data |


## How to Setup this Project


1. Create a virtual environment.

```powershell
py -m venv venv
```

If `py` is not available, use your installed Python executable.

```powershell
python -m venv venv
```

2. Activate the virtual environment.

```powershell
.\venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
pip install -r requirements.txt
```

4. Create or update the `.env` file in the project root.

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=training_db
```

5. Make sure MySQL is running and the database exists.

```sql
CREATE DATABASE training_db;
```

6. Place all document templates in:

```text
app/views/templates/
```

## Environment Variables

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `DB_HOST` | No | `localhost` | MySQL host address |
| `DB_USER` | No | `root` | MySQL username |
| `DB_PASSWORD` | No | Empty string | MySQL password |
| `DB_NAME` | No | `training_db` | MySQL database name |

Environment variables are loaded from `.env` by `app/config/database.py`.

## Running the Project

Run the API server from the project root.

```powershell
uvicorn main:app --reload
```

Default local API URL:

```text
http://127.0.0.1:8000
```

Health check route:

```text
GET /
```

Interactive API docs:

```text
http://127.0.0.1:8000/docs
```

All application API routes use this prefix:

```text
/api/v1
```

## API Routes

### Root

| Method | Path | Description |
| --- | --- | --- |
| GET | `/` | Check that the server is running |

### Authentication

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/auth/login` | Login and set session cookie |

### Admin Users

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/admin/users` | List users |
| POST | `/api/v1/admin/users` | Create user |
| PUT | `/api/v1/admin/users/{user_id}` | Update user |
| DELETE | `/api/v1/admin/users/{user_id}` | Delete user |

### Template Management

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/admin/templates` | List available document templates |
| GET | `/api/v1/admin/templates/{filename}/download` | Download a template |
| POST | `/api/v1/admin/templates/{filename}/upload` | Upload and replace a template |

### Training Batches

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/training_batches` | Create training batch |
| GET | `/api/v1/training_batches` | List training batches |
| GET | `/api/v1/training_batches/detail/{batch_code}` | Get training batch detail |
| PUT | `/api/v1/training_batches/{id}` | Update training batch |
| DELETE | `/api/v1/training_batches/{id}` | Delete training batch |

### Applicants

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/applicants/bulk` | Create applicants in bulk |
| GET | `/api/v1/applicants` | List applicants |
| GET | `/api/v1/applicants/{id}` | Get applicant by ID |
| PUT | `/api/v1/applicants/bulk-update-result` | Update applicant results in bulk |
| PUT | `/api/v1/applicants/{id}` | Update applicant |
| GET | `/api/v1/applicants/batch/{batch_code}` | List applicants by training batch |
| DELETE | `/api/v1/applicants/{id}` | Delete applicant |

### Master Courses

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/master_courses` | Create course |
| GET | `/api/v1/master_courses` | List courses |
| GET | `/api/v1/master_courses/{id}` | Get course by ID |
| PUT | `/api/v1/master_courses/{id}` | Update course |
| DELETE | `/api/v1/master_courses/{id}` | Delete course |

### Instructors

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/instructors` | Create instructor |
| GET | `/api/v1/instructors` | List instructors |
| GET | `/api/v1/instructors/{id}` | Get instructor by ID |
| PUT | `/api/v1/instructors/{id}` | Update instructor |
| DELETE | `/api/v1/instructors/{id}` | Delete instructor |

### Locations

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/locations` | Create location |
| GET | `/api/v1/locations` | List locations |
| GET | `/api/v1/locations/{id}` | Get location by ID |
| PUT | `/api/v1/locations/{id}` | Update location |
| DELETE | `/api/v1/locations/{id}` | Delete location |

### Staff

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/staff` | Create staff |
| GET | `/api/v1/staff` | List staff |
| GET | `/api/v1/staff/{id}` | Get staff by ID |
| PUT | `/api/v1/staff/{id}` | Update staff |
| DELETE | `/api/v1/staff/{id}` | Delete staff |

### Project Activities, Plans, and Projects

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/project_activities` | Create project activity |
| GET | `/api/v1/project_activities` | List project activities |
| GET | `/api/v1/project_activities/{id}` | Get project activity by ID |
| PUT | `/api/v1/project_activities/{id}` | Update project activity |
| DELETE | `/api/v1/project_activities/{id}` | Delete project activity |
| POST | `/api/v1/master_plans` | Create master plan |
| GET | `/api/v1/master_plans` | List master plans |
| PUT | `/api/v1/master_plans/{id}` | Update master plan |
| DELETE | `/api/v1/master_plans/{id}` | Delete master plan |
| POST | `/api/v1/master_projects` | Create master project |
| GET | `/api/v1/master_projects` | List master projects |
| PUT | `/api/v1/master_projects/{id}` | Update master project |
| DELETE | `/api/v1/master_projects/{id}` | Delete master project |

### Calendar Events

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/events` | List events |
| GET | `/api/v1/events/{id}` | Get event by ID |
| POST | `/api/v1/events` | Create event |
| PUT | `/api/v1/events/{id}` | Update event |
| DELETE | `/api/v1/events/{id}` | Delete event |
| DELETE | `/api/v1/events-cleanup` | Delete expired events |

### Loan Records

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/v1/loan/update-clearance` | Update loan clearance data |
| GET | `/api/v1/loans` | List loans |
| GET | `/api/v1/loan/batch/{batch_code}` | Get loan by batch code |
| DELETE | `/api/v1/loan/batch/{batch_code}` | Delete loan by batch code |

### Document Generation

| Method | Path | Description |
| --- | --- | --- |
| GET | `/api/v1/generate-doc/{batch_code}` | Generate approval training document |
| GET | `/api/v1/generate-schedule/{batch_code}` | Generate applicant schedule document |
| GET | `/api/v1/Material/{batch_code}` | Generate material document |
| GET | `/api/v1/generate-food/{batch_code}` | Generate food loan document |
| GET | `/api/v1/generate-food-snack/{batch_code}` | Generate snack loan document |
| GET | `/api/v1/generate-inst/{batch_code}` | Generate instructor loan document |
| GET | `/api/v1/complete/{batch_code}` | Generate completion announcement document |
| GET | `/api/v1/summary/{batch_code}` | Generate loan summary document |
| GET | `/api/v1/generate-all/{batch_code}` | Generate all related documents as a ZIP file |

## Folder Structure

```text
Myproject/
+-- app/
|   +-- config/
|   |   +-- __init__.py
|   |   +-- database.py
|   |   +-- settings.py
|   +-- controllers/
|   |   +-- activity_router.py
|   |   +-- admin_router.py
|   |   +-- allow_practice.py
|   |   +-- applicants.py
|   |   +-- auth_router.py
|   |   +-- batch_router.py
|   |   +-- borrow_food.py
|   |   +-- borrow_food_snack.py
|   |   +-- borrow_inst.py
|   |   +-- calender_router.py
|   |   +-- can_applicant.py
|   |   +-- complete_std.py
|   |   +-- courses.py
|   |   +-- GenWord.py
|   |   +-- instructors.py
|   |   +-- loan_router.py
|   |   +-- locations.py
|   |   +-- material.py
|   |   +-- staff.py
|   |   +-- Summary_of_the_loan.py
|   |   +-- template_router.py
|   +-- models/
|   |   +-- activity_model.py
|   |   +-- applicant_model.py
|   |   +-- auth_model.py
|   |   +-- batch_model.py
|   |   +-- calender_model.py
|   |   +-- course_model.py
|   |   +-- instructors_model.py
|   |   +-- loan_model.py
|   |   +-- locations_model.py
|   |   +-- staff_model.py
|   +-- views/
|       +-- templates/
|           +-- Template.docx
|           +-- applicant.docx
|           +-- announce_date.docx
|           +-- food_borrow.docx
|           +-- food_snack_borrow.docx
|           +-- inst_borrow.docx
|           +-- material.docx
|           +-- refund_summary.docx
+-- .env
+-- .gitignore
+-- index.html
+-- main.py
+-- README.md
+-- requirements.txt
+-- reset_password.py
```

## Notes

- Startup cleanup runs when the FastAPI app starts and deletes expired calendar events.
- CORS is currently configured for `http://127.0.0.1:5500`.
- Generated files are returned as downloads by the API.
- Template files are read from `app/views/templates`.
- Admin template upload routes require a valid admin session cookie.
