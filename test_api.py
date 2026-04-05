"""Quick end-to-end smoke test for the Finance API."""
import urllib.request
import urllib.error
import json

BASE = "http://localhost:8001"


def request(method, path, data=None, token=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(data).encode() if data else None,
        headers={"Content-Type": "application/json"} if data else {},
        method=method,
    )
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            body = r.read()
            return r.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read()
        return e.code, json.loads(body) if body else {}


def post(path, data, token=None):
    return request("POST", path, data, token)

def get(path, token=None):
    return request("GET", path, token=token)

def put(path, data, token=None):
    return request("PUT", path, data, token)

def delete(path, token=None):
    return request("DELETE", path, token=token)


print("=" * 50)
print("Finance API Smoke Tests")
print("=" * 50)

# 1. Health check
status, body = get("/")
assert status == 200
print(f"[PASS] Health check: {body['status']}")

import time
uid = int(time.time())
admin_email = f"admin_{uid}@test.com"
viewer_email = f"viewer_{uid}@test.com"
analyst_email = f"analyst_{uid}@test.com"

# 2. Register admin
status, body = post("/auth/register", {"email": admin_email, "password": "pass123", "role": "ADMIN"})
assert status == 201, f"Expected 201, got {status}: {body}"
admin_token = body["access_token"]
print("[PASS] Register admin")

# 3. Register viewer
status, body = post("/auth/register", {"email": viewer_email, "password": "pass123", "role": "VIEWER"})
assert status == 201, f"Expected 201, got {status}: {body}"
viewer_token = body["access_token"]
print("[PASS] Register viewer")

# 4. Register analyst
status, body = post("/auth/register", {"email": analyst_email, "password": "pass123", "role": "ANALYST"})
assert status == 201, f"Expected 201, got {status}: {body}"
analyst_token = body["access_token"]
print("[PASS] Register analyst")

# 5. Duplicate email should fail
status, body = post("/auth/register", {"email": admin_email, "password": "x", "role": "ADMIN"})
assert status == 400, f"Expected 400, got {status}"
print("[PASS] Duplicate email rejected")

# 6. Login
status, body = post("/auth/login", {"email": admin_email, "password": "pass123"})
assert status == 200
print("[PASS] Login")

# 7. Wrong password
status, body = post("/auth/login", {"email": admin_email, "password": "wrong"})
assert status == 401
print("[PASS] Wrong password rejected")

# 8. Create records (admin)
records = [
    {"amount": 5000.0, "type": "INCOME",  "category": "Salary",   "date": "2024-01-15"},
    {"amount": 1200.0, "type": "EXPENSE", "category": "Rent",     "date": "2024-01-16"},
    {"amount": 300.0,  "type": "EXPENSE", "category": "Food",     "date": "2024-01-17"},
    {"amount": 800.0,  "type": "INCOME",  "category": "Freelance","date": "2024-01-18"},
]
created_ids = []
for rec in records:
    status, body = post("/records", rec, admin_token)
    assert status == 201, f"Expected 201, got {status}: {body}"
    created_ids.append(body["id"])
print(f"[PASS] Created {len(records)} financial records")

# 9. Viewer create record => 403
status, body = post("/records", {"amount": 99, "type": "EXPENSE", "category": "Food", "date": "2024-01-19"}, viewer_token)
assert status == 403, f"Expected 403, got {status}"
print("[PASS] Viewer blocked from creating records")

# 10. Analyst reads records
status, body = get("/records", analyst_token)
assert status == 200
print(f"[PASS] Analyst can read {len(body)} records")

# 11. Viewer reads records => 403
status, body = get("/records", viewer_token)
assert status == 403
print("[PASS] Viewer blocked from reading records")

# 12. Filter records by type
status, body = get("/records?type=INCOME", analyst_token)
assert status == 200 and all(r["type"] == "INCOME" for r in body)
print(f"[PASS] Filter by type=INCOME: {len(body)} records")

# 13. Filter records by category
status, body = get("/records?category=food", analyst_token)
assert status == 200
print(f"[PASS] Filter by category=food: {len(body)} records")

# 14. Dashboard accessible by all roles
for role_name, token in [("Viewer", viewer_token), ("Analyst", analyst_token), ("Admin", admin_token)]:
    status, body = get("/dashboard/summary", token)
    assert status == 200, f"{role_name} dashboard failed: {body}"
print(f"[PASS] Dashboard accessible to Viewer, Analyst, Admin")

# 15. Check dashboard values
status, body = get("/dashboard/summary", admin_token)
assert body["total_income"] == 5800.0
assert body["total_expenses"] == 1500.0
assert body["net_balance"] == 4300.0
print(f"[PASS] Dashboard values correct: income={body['total_income']}, expenses={body['total_expenses']}, net={body['net_balance']}")
print(f"       Category totals: {body['category_totals']}")
print(f"       Recent records: {len(body['recent_records'])}")

# 16. Update a record (admin)
status, body = put(f"/records/{created_ids[0]}", {"amount": 6000.0, "notes": "Updated salary"}, admin_token)
assert status == 200 and body["amount"] == 6000.0
print("[PASS] Admin updated a record")

# 17. Analyst tries to update => 403
status, body = put(f"/records/{created_ids[0]}", {"amount": 999.0}, analyst_token)
assert status == 403
print("[PASS] Analyst blocked from updating records")

# 18. Delete a record (admin)
status, _ = delete(f"/records/{created_ids[-1]}", admin_token)
assert status == 204
print("[PASS] Admin deleted a record")

# 19. Delete non-existent record => 404
status, body = delete("/records/99999", admin_token)
assert status == 404
print("[PASS] Delete non-existent record returns 404")

# 20. Admin lists users
status, body = get("/users", admin_token)
assert status == 200
print(f"[PASS] Admin lists {len(body)} users")

# 21. Analyst lists users => 403
status, body = get("/users", analyst_token)
assert status == 403
print("[PASS] Analyst blocked from listing users")

# 22. Admin updates user role
viewer = next(u for u in body if "viewer" in u["email"])
status, body = put(f"/users/{viewer['id']}/role", {"role": "ANALYST"}, admin_token)
assert status == 200 and body["role"] == "ANALYST"
print("[PASS] Admin promoted viewer to analyst")

# 23. Admin deactivates a user
status, body = put(f"/users/{viewer['id']}/status", {"status": "INACTIVE"}, admin_token)
assert status == 200 and body["status"] == "INACTIVE"
print("[PASS] Admin deactivated a user")

# 24. Inactive user token should be rejected
status, body = get("/dashboard/summary", viewer_token)
assert status == 403
print("[PASS] Inactive user cannot access API")

print()
print("=" * 50)
print("All 24 tests passed!")
print("=" * 50)
