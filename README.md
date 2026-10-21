# LedgerForge — Employee, Payroll & Accounting API

LedgerForge is a Python-based backend project developed as part of the Aura Workforce Python Developers training track. It begins with a working FastAPI skeleton and evolves into an employee management, attendance, payroll, and accounting platform over four weeks.

**Current version:** v0.0.1  
**Current milestone:** LF-01 — Project Bootstrap & Repository Setup  
**Technology:** Python, FastAPI, SQLAlchemy, Pydantic, SQLite (starter configuration), Git and Pytest

> **Training project:** All company and business data used in LedgerForge is fictional and intended for learning purposes only.

## Features Available in the Starter Project

- FastAPI application with interactive Swagger documentation.
- Health-check endpoint at `GET /health`.
- Department listing and department lookup endpoints.
- SQLAlchemy model for the Department entity.
- Example CSV data seeder.
- Environment-based application configuration.
- Automated tests using Pytest.
- Git version control and GitHub repository integration.

## Prerequisites

Install the following before starting:

- Python 3.11 or newer.
- Git.
- Visual Studio Code or another Python IDE.
- A terminal such as PowerShell, Command Prompt, or Bash.

Python 3.12 is recommended for this project setup.

## Getting Started — 8 Steps

### 1. Clone the repository

```bash
git clone https://github.com/Sudharsana27/05_Starter_Project.git
cd 05_Starter_Project
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use the following for the current terminal session if needed:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create your local `.env` file from the example.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**macOS/Linux:**

```bash
cp .env.example .env
```

Review `.env` and adjust values if necessary. Never commit `.env` or expose secret keys.

### 6. Seed the example data

```bash
python -m scripts.seed_example
```

This loads the starter project's example department data into the configured database.

### 7. Start the API

```bash
uvicorn app.main:app --reload
```

The development server should be available at:

- API base URL: http://127.0.0.1:8000
- Interactive Swagger documentation: http://127.0.0.1:8000/docs
- OpenAPI schema: http://127.0.0.1:8000/openapi.json

Keep the terminal running while using the API. Press `Ctrl+C` to stop the server.

### 8. Run the automated tests

Open another terminal, activate the virtual environment, and run:

```bash
pytest
```

The starter project currently contains two tests covering the health endpoint and department functionality. Both should pass.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Checks whether the API is responding |
| GET | `/departments` | Lists available departments |
| GET | `/departments/{department_id}` | Retrieves a department by ID |

Use Swagger at `/docs` to inspect and try the available endpoints.

A successful health-check response looks like this:

```json
{
  "status": "ok"
}
```

An unknown department ID should return HTTP `404 Not Found`.

## Project Structure

```text
05_Starter_Project/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── routers/
│       ├── __init__.py
│       └── departments.py
├── scripts/
│   ├── __init__.py
│   └── seed_example.py
├── tests/
│   ├── __init__.py
│   └── test_departments.py
├── .env.example
├── .gitignore
├── docker-compose.dev.yml
├── requirements.txt
└── README.md
```

## Configuration

Application settings are managed through `app/config.py` and environment variables.

The starter configuration uses SQLite. Later milestones will introduce PostgreSQL, database migrations, and additional configuration for the expanding application.

Keep credentials and environment-specific settings in `.env`, not in source code.

## Development Guidelines

- Create a separate Git branch for each task. For example: `lf-02-employee-model`.
- Write automated tests for every new endpoint and important business rule.
- Use SQLAlchemy models for database entities and Pydantic schemas for API input and output.
- Use `Decimal` rather than `float` for monetary calculations.
- Use migrations to manage database schema changes.
- Never commit `.env`, `.venv`, database files, or other generated secrets and local artifacts.
- Make small, meaningful commits and push completed work to GitHub.

## Git Workflow

Create a branch for the next task:

```bash
git switch -c lf-02-employee-model
```

After making changes, run the tests:

```bash
pytest
```

Review and commit your changes:

```bash
git status
git add .
git commit -m "LF-02: Add employee data model"
git push -u origin lf-02-employee-model
```

Review staged files before committing to ensure no secrets or local environment files are included.

## Roadmap

| Milestone | Scope |
|---|---|
| LF-01 | Project setup, API skeleton, tests and Git repository |
| LF-02 | Employee, department, role and assignment data model |
| LF-03 | One-command data seeding |
| LF-04 | Employee and team APIs |
| LF-05–LF-08 | Salary, attendance, leave, payroll and payslips |
| LF-09–LF-12 | Accounting ledger, invoices, expenses and payroll posting |
| LF-13–LF-16 | Authentication, tax reports, financial reports and release candidate |
| LF-17–LF-20 | Deployment, reliability, exports, final audit and submission |

## Current Status

LF-01 has been implemented with a working API, passing starter tests, a GitHub repository, and the `v0.0.1` release tag.

The next milestone is **LF-02 — Employee & Org Data Model**, which will introduce the core employee-related tables, relationships, PostgreSQL migrations, and an ER diagram.

---

**LedgerForge · Aura Workforce · Python Developers Training Track**