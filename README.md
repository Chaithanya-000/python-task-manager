# TaskMaster Pro – Python Full Stack Task Manager Web Application

[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![ORM](https://img.shields.io/badge/SQLAlchemy-2.0.35-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Pytest-Passing%20(20%2F20)-brightgreen.svg)](https://docs.pytest.org/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](#)

A modern, production-grade, full-stack Task Management application built with **Flask**, **SQLAlchemy**, and **Bootstrap 5**. Designed from the ground up to be modular, production-ready, and optimized for **End-to-End DevOps CI/CD pipelines** utilizing **GitHub Actions**, **Jenkins**, **Docker**, **AWS EC2**, and **Nginx**.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Folder Structure](#folder-structure)
5. [Installation & Setup](#installation--setup)
6. [Database Initialization & Seeding](#database-initialization--seeding)
7. [Running the Application](#running-the-application)
8. [Automated Testing](#automated-testing)
9. [REST API Documentation](#rest-api-documentation)
10. [DevOps & Docker Deployment Readiness](#devops--docker-deployment-readiness)

---

## Project Overview

TaskMaster Pro is an enterprise-styled SaaS task manager providing real-time task orchestration, status auditing, priority categorization, and statistical reporting.

The system is split into two cleanly separated layers:
- **Backend**: Python 3.11+ RESTful API built on Flask and Flask-SQLAlchemy, adhering to application factory design patterns, environment variable configuration, clean error handling, and robust input validation.
- **Frontend**: Responsive, modern SaaS interface styled with Bootstrap 5.3, Inter typography, responsive sidebar navigation, fluid metric cards, and asynchronous Fetch API interactivity.

---

## Key Features

- **Task Lifecycle Management**: Create, view, edit, delete, and toggle tasks between `Pending` and `Completed`.
- **Search & Filter Engine**: Live keyword search across task titles and descriptions with debounce; filter instantly by status (`Pending`, `Completed`) and priority (`High`, `Medium`, `Low`).
- **Interactive Metrics Dashboard**: Live stat cards tracking Total Tasks, Pending Tasks, Completed Tasks, and dynamic Task Completion Percentage with visual progress bar.
- **Dual View Modes**: Switch seamlessly between a high-density Table View and an agile Card Grid View.
- **Health Check API**: Dedicated `/health` endpoint validating database connectivity and system status for load balancers and container orchestrators.
- **Persistent Storage**: Robust SQLite configuration stored in the `instance/` folder with support for Docker volume mounting and external PostgreSQL/MySQL through `DATABASE_URL`.
- **Zero-Flicker Optimistic UI**: Bootstrap toast alerts, responsive modals, and instant UI state updates without page reloads.

---

## Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.11+, Flask 3.0.3, Flask-SQLAlchemy 3.1.1, SQLAlchemy 2.0.35 |
| **WSGI / Production Server** | Gunicorn 22.0.0 (Linux/Docker/EC2) |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons 1.11.3 |
| **Database** | SQLite3 (Persistent local/container storage), SQLAlchemy ORM |
| **Configuration** | `python-dotenv` 1.0.1 (12-Factor App methodology) |
| **Automated Testing** | Pytest 8.3.3, Flask Test Client |

---

## Folder Structure

```
python-task-manager/
│
├── app.py                  # Application factory, routes, and WSGI entry point
├── config.py               # Environment configuration (Dev, Test, Prod)
├── models.py               # SQLAlchemy Task model and database instance
├── requirements.txt        # Pinned production and test dependencies
├── .env.example            # Sample environment variables template
├── .gitignore              # Git ignore rules for Python, DBs, and virtualenvs
├── README.md               # Complete architecture & deployment guide
│
├── templates/              # Jinja2 template views
│   ├── base.html           # Master layout (sidebar, top navbar, toasts)
│   ├── index.html          # Dashboard, modals, table & grid containers
│   └── components/
│       └── stats.html      # Metrics cards reusable component
│
├── static/                 # Static web assets
│   ├── css/
│   │   └── style.css       # Custom SaaS design system & theme variables
│   ├── js/
│   │   └── script.js       # Asynchronous REST API client & DOM renderer
│   └── images/             # Static icons and logos
│
├── tests/                  # Automated Pytest test suite
│   ├── conftest.py         # Pytest fixtures and isolated in-memory DB
│   └── test_app.py         # 20 unit and integration tests
│
└── instance/               # Local SQLite persistent database location
    └── tasks.db            # Generated SQLite database file
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.11 or higher installed (`python --version`)
- Git installed (`git --version`)

### 2. Clone the Repository
```bash
git clone https://github.com/<your-username>/python-task-manager.git
cd python-task-manager
```

### 3. Create and Activate Virtual Environment

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (Command Prompt / PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to create your local `.env`:
```bash
cp .env.example .env
```

Default contents of `.env`:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=dev-secret-key-taskmaster-2026
PORT=5000
HOST=0.0.0.0
# DATABASE_URL=sqlite:///instance/tasks.db
```

---

## Database Initialization & Seeding

The application automatically verifies and initializes SQLite tables on startup. For explicit control in deployment scripts or CI/CD pipelines, custom CLI commands are available:

### Initialize Empty Database
```bash
flask init-db
```

### Seed Database with Sample DevOps Tasks
```bash
flask seed-db
```

---

## Running the Application

### Local Development Mode
```bash
python app.py
```
Or with the Flask CLI:
```bash
flask run --host=0.0.0.0 --port=5000
```
Open [http://localhost:5000](http://localhost:5000) in your web browser.

### Production WSGI Mode (Linux / Docker / AWS EC2)
For production environments, run using **Gunicorn**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"
```

Key Gunicorn parameters:
- `-w 4`: Spawns 4 worker processes.
- `-b 0.0.0.0:5000`: Binds to all network interfaces on port 5000.
- `"app:create_app()"`: Utilizes the application factory for clean thread isolation.

---

## Automated Testing

The project includes an automated **Pytest** suite covering startup, health checks, REST endpoints, input validations, error states, and database persistence.

Tests execute against an **isolated in-memory SQLite database** (`sqlite:///:memory:`) so development data is never modified.

### Run All Tests
```bash
pytest -v
```

### Run Tests with Detailed Coverage (if pytest-cov installed)
```bash
pytest --cov=. -v
```

### Verified Test Cases (20 Passing)
- `test_app_startup_and_config` – Verifies testing configuration and in-memory DB isolation.
- `test_health_check_endpoint` – Tests `/health` returns HTTP 200 with database check.
- `test_homepage_dashboard` – Confirms dashboard page renders correctly.
- `test_create_task_success` – Validates task creation with Low, Medium, and High priorities.
- `test_create_task_validation_missing_title` – Validates 400 error on blank title.
- `test_create_task_validation_invalid_priority` – Validates 400 error on invalid priority.
- `test_create_task_validation_invalid_status` – Validates 400 error on invalid status.
- `test_get_all_tasks` – Verifies retrieval of task collection.
- `test_get_single_task_success` – Verifies retrieval by task ID.
- `test_get_single_task_not_found` – Verifies 404 response on unknown task ID.
- `test_edit_task_success` – Tests PUT/PATCH updates to title, description, priority, and status.
- `test_edit_task_invalid_input` – Verifies 400 error when editing with invalid payload.
- `test_toggle_task_status` – Tests one-click status flipping between Pending and Completed.
- `test_delete_task` – Verifies record deletion and subsequent 404 confirmation.
- `test_search_tasks_by_title_and_description` – Verifies ILIKE keyword search logic.
- `test_filter_tasks_by_status` – Verifies query filtering by status (`Pending`/`Completed`).
- `test_filter_tasks_by_priority` – Verifies query filtering by priority level.
- `test_statistics_endpoint` – Verifies count math and task completion percentage.
- `test_cli_seed_and_init` – Tests Flask CLI integration commands.
- `test_database_persistence_across_app_restarts` – Simulates app shutdown and disk reload.

---

## REST API Documentation

All API responses return standard JSON.

### Base URL: `/api`

| Method | Endpoint | Description | Request Body |
|---|---|---|---|
| `GET` | `/health` | Application & DB health status | None |
| `GET` | `/api/stats` | Summary statistics & completion rate | None |
| `GET` | `/api/tasks` | Get all tasks (supports query params) | None |
| `POST` | `/api/tasks` | Create a new task | `{ title, description?, priority?, status? }` |
| `GET` | `/api/tasks/<id>` | Get task by ID | None |
| `PUT` | `/api/tasks/<id>` | Full update of task | `{ title?, description?, priority?, status? }` |
| `PATCH` | `/api/tasks/<id>` | Partial update of task | `{ title?, description?, priority?, status? }` |
| `PATCH` | `/api/tasks/<id>/status` | Toggle or set task status | `{ status?: "Completed" \| "Pending" }` |
| `DELETE` | `/api/tasks/<id>` | Delete task by ID | None |

### Query Parameters for `GET /api/tasks`
- `search` (string): Search filter matching task title or description.
- `status` (`All` | `Pending` | `Completed`): Filter by task status.
- `priority` (`All` | `High` | `Medium` | `Low`): Filter by priority.
- `sort_by` (`created_at` | `updated_at` | `priority` | `title`): Sort column (default: `created_at`).
- `order` (`asc` | `desc`): Sort direction (default: `desc`).

### Example Responses

#### `GET /health`
```json
{
  "database": "connected",
  "status": "healthy",
  "timestamp": "2026-11-20T11:47:46.137858+00:00",
  "version": "1.0.0"
}
```

#### `GET /api/stats`
```json
{
  "total": 6,
  "completed": 2,
  "pending": 4,
  "completion_percentage": 33.3,
  "priority_breakdown": {
    "high": 3,
    "medium": 2,
    "low": 1
  }
}
```

#### `POST /api/tasks`
**Request:**
```json
{
  "title": "Configure Nginx reverse proxy",
  "description": "Forward port 80 to 5000",
  "priority": "High",
  "status": "Pending"
}
```
**Response (HTTP 201 Created):**
```json
{
  "message": "Task created successfully.",
  "task": {
    "id": 1,
    "title": "Configure Nginx reverse proxy",
    "description": "Forward port 80 to 5000",
    "priority": "High",
    "status": "Pending",
    "created_at": "2026-11-20 11:48:01",
    "created_at_iso": "2026-11-20T11:48:01.517830",
    "updated_at": "2026-11-20 11:48:01",
    "updated_at_iso": "2026-11-20T11:48:01.517843"
  }
}
```

---

## DevOps & Docker Deployment Readiness

This application is engineered specifically for future deployment using Docker, Jenkins, Nginx, and AWS EC2:

1. **Host & Port Parameterization**: Listens on `0.0.0.0` and dynamically reads `PORT` from environment variables (default `5000`).
2. **Health Check Probing**: Dedicated `/health` endpoint allows Docker, Kubernetes, and AWS Application Load Balancers (ALB) to monitor container and database health with HTTP 200 checks.
3. **Storage Persistence**: SQLite database is isolated inside the `instance/` folder. When running inside Docker, mount a volume to `/app/instance` to persist database records across container recreations.
4. **Production WSGI Entrypoint**: Module-level application factory `app:create_app()` is fully compatible with Gunicorn, uWSGI, and ASGI wrappers.
5. **Clean Dependency Separation**: `requirements.txt` strictly pins versions for deterministic builds in Jenkins and Docker build stages.
6. **No External Dependencies Outside Repo**: All assets, configs, templates, and scripts reside self-contained inside the project root.

---

## License

This project is open-source and available under the [MIT License](LICENSE).
