from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from database import engine, Base
from routers import auth, users, records, dashboard

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Dashboard API",
    description="Role-based finance data backend for a dashboard system.",
    version="1.0.0",
    redirect_slashes=False,
)

# including routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


# global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Finance API is running"}
