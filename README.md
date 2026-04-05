# Finance Dashboard API

A simple, clean REST API backend for a role-based finance dashboard system.

## Stack

| Concern | Choice |
|---|---|
| Language | Python 3.11+ |
| Framework | FastAPI |
| Database | SQLite (file: `finance.db`) |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| Auth | JWT via `python-jose` + `passlib` (bcrypt) |

---

## Project Structure

```text
.
├── main.py             # Application entry point
├── database.py         # SQLAlchemy setup
├── models.py           # Database SQLAlchemy models
├── schemas.py          # Pydantic validation models
├── auth.py             # JWT auth and hashing
├── dependencies.py     # FastAPI dependencies (auth, db)
├── routers/            # API route definitions
│   ├── auth.py         # Auth endpoints
│   ├── dashboard.py    # Analytics endpoints
│   ├── records.py      # CRUD for records
│   └── users.py        # User management
└── test_api.py         # Basic integration tests
```

---

## Setup & Run

### 1. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the server

```bash
uvicorn main:app --reload
```

The API will be available at **http://localhost:8000**

Interactive API docs with swagger UI will be at: **http://localhost:8000/docs**

---

## Roles & Permissions

| Action | VIEWER | ANALYST | ADMIN |
|---|:---:|:---:|:---:|
| GET /dashboard/summary | Yes | Yes | Yes |
| GET /records | No | Yes | Yes |
| POST /records | No | No | Yes |
| PUT /records/:id | No | No | Yes |
| DELETE /records/:id | No | No | Yes |
| GET /users | No | No | Yes |
| PUT /users/:id/role | No | No | Yes |
| PUT /users/:id/status | No | No | Yes |

---

## API Overview

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a user (role optional, defaults to VIEWER) |
| POST | `/auth/login` | Login and receive a JWT token |

**Register body:**
```json
{
  "email": "admin@example.com",
  "password": "secret123",
  "role": "ADMIN"
}
```

**Login response:**
```json
{
  "access_token": "<JWT_TOKEN>",
  "token_type": "bearer"
}
```

Use the token in the `Authorization` header for all protected routes:
```
Authorization: Bearer <JWT_TOKEN>
```

---

### Users (Admin only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/users` | List all users |
| PUT | `/users/{id}/role` | Update a user's role |
| PUT | `/users/{id}/status` | Activate or deactivate a user |

---

### Financial Records
| Method | Endpoint | Description |
|---|---|---|
| GET | `/records` | List records (Analyst, Admin) |
| POST | `/records` | Create a record (Admin) |
| PUT | `/records/{id}` | Update a record (Admin) |
| DELETE | `/records/{id}` | Delete a record (Admin) |

**GET /records query filters:**
- `type` — `INCOME` or `EXPENSE`
- `category` — partial text match
- `date_from` — `YYYY-MM-DD`
- `date_to` — `YYYY-MM-DD`
- `page` — page number (default: 1)
- `limit` — records per page (default: 20, max: 100)

**POST /records body:**
```json
{
  "amount": 5000.00,
  "type": "INCOME",
  "category": "Salary",
  "date": "2024-01-15",
  "notes": "January salary"
}
```

---

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary` | Aggregated summary (all roles) |

**Response includes:**
- `total_income` — sum of all INCOME records
- `total_expenses` — sum of all EXPENSE records
- `net_balance` — income - expenses
- `category_totals` — per-category sum
- `recent_records` — last 5 records by date

---

## Assumptions & Design Decisions

1. **SQLite** is used for simplicity. Provides a zero-configuration database that is easy for evaluators to run. It can be easily swapped with PostgreSQL by changing `DATABASE_URL`.
2. **Admin Registration**: The system allows passing `"role": "ADMIN"` during registration for easy setup. In production, this would be restricted.
3. **Authentication**: JWT is used for stateless authentication. Tokens expire after 8 hours.
4. **Inactive Users**: User status checking is implemented. Inactive users receive `403 Forbidden` on protected routes.
5. **Database Initialization**: Tables are automatically created on startup via SQLAlchemy `create_all`. Alembic isn't used to keep the setup step minimal.

## Trade-offs Considered

- **Soft vs Hard Deletes**: Records are permanently deleted from the database. This keeps the queries simple and focuses on basic CRUD operations, though soft deletes would be safer in production context.
- **Pagination Strategy**: Used standard limit/offset pagination rather than cursor-based. It is simpler to implement and sufficiently performant for the scope of a dashboard.
- **Role Verification**: Roles are checked explicitly in route dependencies (e.g., `require_admin`). While a more complex ACL (Access Control List) system could offer finer granularity, explicit role checks provide better readability and simplicity for this scale.
- **Inline Error Handling**: Simple HTTPException calls are used throughout the endpoints instead of a centralized exception handler to keep the logic easy to follow linearly.
