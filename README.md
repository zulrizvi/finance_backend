# Finance Dashboard API

REST API backend for a role-based finance dashboard system

## Tech Stack used

| Component | Choice |
|---|---|
| Framework | FastAPI (Python 3.11+) |
| Database | SQLite |
| ORM | SQLAlchemy |
| Validation | Pydantic v2 |
| Authentication | JWT via `python-jose` & `passlib` |

---

## Local Setup

Since this application is primarily deployed on Render, local setup is kept to the absolute minimum.


The API will be available at **http://localhost:8000**.
Interactive API documentation (Swagger UI) is automatically generated at **http://localhost:8000/docs**.

---

## Roles & Permissions

Granular access control ensuring secure data management:

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
| POST | `/auth/register` | Register a new user (role defaults to `VIEWER` if unspecified). |
| POST | `/auth/login` | Authenticate and obtain a JWT bearer token. |

Use the obtained token in the `Authorization` header for all protected routes:
`Authorization: Bearer <JWT_TOKEN>`

---

### Dashboard
| Method | Endpoint | Description |
|---|---|---|
| GET | `/dashboard/summary` | Aggregated summary of income, expenses, and category totals. Accessible to all roles. |

---

### Financial Records
| Method | Endpoint | Description |
|---|---|---|
| GET | `/records` | List records with optional filters (Analyst, Admin). |
| POST | `/records` | Create a new financial record (Admin). |
| PUT | `/records/{id}` | Update an existing financial record (Admin). |
| DELETE | `/records/{id}` | Delete a financial record (Admin). |

**Supported Filters (`GET /records`):**
- `type`: `INCOME` or `EXPENSE`
- `category`: Partial text lookup
- `date_from` / `date_to`: `YYYY-MM-DD`
- `page` / `limit`: Pagination controls

---

### Users (Admin Only)
| Method | Endpoint | Description |
|---|---|---|
| GET | `/users` | List all users. |
| PUT | `/users/{id}/role` | Grant or revoke roles (e.g., promote to `ADMIN`). |
| PUT | `/users/{id}/status` | Activate or deactivate a user account. |

---

## Assumptions & Design Decisions

1. **SQLite Database**: Chosen for complete simplicity, offering a zero-configuration database that works natively in the local environment and deployed platforms without external dependencies.
2. **Admin Bootstrapping**: The system intentionally allows passing `"role": "ADMIN"` during registration purely to facilitate easy testing and initial setup.
3. **Stateless Authentication**: JWT evaluates authenticity and expiration locally without needing a stateful session store. Tokens expire after 8 hours.
4. **Inactive Users**: User status checking is actively enforced. Deactivated users automatically receive a `403 Forbidden` rejection on protected routes.
5. **Database Initialization**: Tables are automatically evaluated and created on startup via SQLAlchemy `create_all`. Migrations (like Alembic) are omitted to keep the app lifecycle extremely simple.

## Trade-offs Considered

- **Hard Deletions vs. Soft Deletes**: Records are permanently deleted from the database to aggressively prioritize simplicity across CRUD operations. Soft deletes would be implemented for a larger, audit-heavy production context.
- **Limit/Offset Pagination**: Standard offset pagination is used instead of cursor-based pagination. It provides straightforward logic and is highly performant for the realistic volume of a personal dashboard database.
- **Explicit Role Verification**: Roles are enforced explicitly in FastAPI route dependencies rather than a dense Access Control List (ACL) matrix. This provides maximum code readability and linear control flow.
- **Inline Error Handling**: Endpoints handle logical failures and dispatch explicit `HTTPException` rules internally. This allows developers to follow route execution without navigating through centralized exception handlers.
