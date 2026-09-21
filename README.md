# Taskie — Task Management System API

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1%2B-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.15%2B-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

A containerized, production-ready Task Management System REST API built with Django, Django REST Framework (DRF), and PostgreSQL.

---

## Features

- **User Authentication & Profiles:**
  - Secure JWT authentication (`access` and `refresh` tokens via `djangorestframework-simplejwt`).
  - User registration with password validation and user listing for task assignment.
- **Task Management:**
  - Full CRUD operations on tasks.
  - Custom actions: task assignment (`/api/v1/tasks/{id}/assign/`) and completion (`/api/v1/tasks/{id}/complete/`).
  - Filtering by `status` (`TODO`, `IN_PROGRESS`, `DONE`), `priority` (`LOW`, `MEDIUM`, `HIGH`), `assigned_to`, and `created_by`.
  - Full-text search on task titles and descriptions.
  - Flexible ordering by `created_at`, `due_date`, `priority`, `status`, and `title`.
- **Task Comments Subsystem:**
  - Create and list comments per task (`/api/v1/tasks/{id}/comments/`).
  - Retrieve, edit, and delete individual comments (`/api/v1/comments/{id}/`).
  - Author-only permissions for edits and author/task-creator permissions for deletions.
- **Interactive OpenAPI 3.0 Documentation:**
  - Swagger UI: `/api/docs/swagger/`
  - ReDoc: `/api/docs/redoc/`
  - OpenAPI Schema: `/api/schema/`
- **Quality & Containerization:**
  - Self-contained Docker and Docker Compose orchestration with PostgreSQL 16 healthchecks.
  - Automated test suite with `pytest-django` (>90% coverage).
  - PEP 8 compliant, Ruff formatting and linting, static type checking with `ty`.

---

## Quick Start with Docker Compose

Run the entire application and PostgreSQL database with a single command:

```bash
docker-compose up --build
```

The web application will be accessible at:
- **API Base:** `http://localhost:8000/api/v1/`
- **Swagger UI:** `http://localhost:8000/api/docs/swagger/`
- **ReDoc:** `http://localhost:8000/api/docs/redoc/`

---

## Local Development Setup

### 1. Prerequisites
- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv)

### 2. Install Dependencies
```bash
uv sync
```

### 3. Run Migrations
```bash
uv run python manage.py migrate
```

### 4. Start Development Server
```bash
uv run python manage.py runserver
```

---

## Running Tests & Quality Checks

Run the automated test suite with coverage:
```bash
make test
# Or directly:
uv run pytest --cov=src --cov-report=term-missing
```

Run code quality tools (Ruff linting, formatting, static type checking, deptry):
```bash
make check
```

---

## API Reference

### Authentication & Users (`/api/v1/auth/`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/register/` | Register a new user | No |
| `POST` | `/api/v1/auth/token/` | Obtain JWT access & refresh tokens | No |
| `POST` | `/api/v1/auth/token/refresh/` | Refresh JWT access token | No |
| `GET` | `/api/v1/auth/users/` | List registered users for assignment | Yes (Bearer) |
| `GET` | `/api/v1/auth/users/{id}/` | Retrieve user details | Yes (Bearer) |

### Tasks (`/api/v1/tasks/`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/tasks/` | List tasks (supports filtering, search, ordering, pagination) | Yes (Bearer) |
| `POST` | `/api/v1/tasks/` | Create a new task (creator is automatically `request.user`) | Yes (Bearer) |
| `GET` | `/api/v1/tasks/{id}/` | Retrieve task details | Yes (Bearer) |
| `PUT` / `PATCH` | `/api/v1/tasks/{id}/` | Update task details | Yes (Bearer) |
| `DELETE` | `/api/v1/tasks/{id}/` | Delete task | Yes (Bearer) |
| `POST` | `/api/v1/tasks/{id}/complete/` | Mark task as `DONE` | Yes (Bearer) |
| `POST` | `/api/v1/tasks/{id}/assign/` | Assign or reassign task to a user | Yes (Bearer) |
| `GET` | `/api/v1/tasks/{id}/comments/` | List comments on the task | Yes (Bearer) |
| `POST` | `/api/v1/tasks/{id}/comments/` | Add a comment to the task | Yes (Bearer) |

### Comments (`/api/v1/comments/`)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/comments/{id}/` | Retrieve comment details | Yes (Bearer) |
| `PATCH` | `/api/v1/comments/{id}/` | Edit comment (restricted to author) | Yes (Bearer) |
| `DELETE` | `/api/v1/comments/{id}/` | Delete comment (restricted to author or task creator) | Yes (Bearer) |

### API Documentation
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/schema/` | OpenAPI 3.0 schema |
| `GET` | `/api/docs/swagger/` | Interactive Swagger UI |
| `GET` | `/api/docs/redoc/` | ReDoc API documentation |
