from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.db import models  # noqa: F401 ensure model registration
from app.core.config import settings
from app.middleware.security import (
    SecurityHeadersMiddleware,
    AuditLoggingMiddleware
)
from app.routers import (
    users, roles, students,
    auth,
    programs,
    enrollments,
    xapi,
    scorm,
    reports,
    attendance,
    skills,
    externships,
    finance,
    payments,
    complaints,
    credentials,
    transcripts,
    modules,
    h5p,
    audit,
    progress,
    leads,
    content,
    documents,
    public_signing,
)

# Configure logging for audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize DB tables (alembic will handle migrations; create_all is safe for first run)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="AADA LMS API", version="1.0")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body = await request.body()
        body_str = body.decode("utf-8", errors="ignore")
    except RuntimeError:
        body_str = "[body already consumed - likely multipart/form-data]"

    logging.error(
        "Validation error on %s: %s | body=%s",
        request.url.path,
        exc.errors(),
        body_str
    )
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# Security middleware (order matters - first added = outermost layer)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(AuditLoggingMiddleware)

# CORS middleware - use environment variable for production flexibility
allowed_origins = [origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")]
default_dev_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

for origin in default_dev_origins:
    if origin and origin not in allowed_origins:
        allowed_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_prefix = "/api"

app.include_router(auth.router, prefix=api_prefix)
app.include_router(programs.router, prefix=api_prefix)
app.include_router(enrollments.router, prefix=api_prefix)
app.include_router(xapi.router, prefix=api_prefix)
app.include_router(scorm.router, prefix=api_prefix)
app.include_router(reports.router, prefix=api_prefix)
app.include_router(attendance.router, prefix=api_prefix)
app.include_router(skills.router, prefix=api_prefix)
app.include_router(externships.router, prefix=api_prefix)
app.include_router(finance.router, prefix=api_prefix)
app.include_router(payments.router, prefix=api_prefix)
app.include_router(complaints.router, prefix=api_prefix)
app.include_router(credentials.router, prefix=api_prefix)
app.include_router(transcripts.router, prefix=api_prefix)
app.include_router(modules.router, prefix=api_prefix)
app.include_router(h5p.router, prefix=api_prefix)
app.include_router(audit.router, prefix=api_prefix)
app.include_router(progress.router, prefix=api_prefix)
app.include_router(users.router, prefix=api_prefix)
app.include_router(students.router, prefix=api_prefix)
app.include_router(roles.router, prefix=api_prefix)
app.include_router(leads.router, prefix=api_prefix)
app.include_router(content.router, prefix=api_prefix)
app.include_router(documents.router, prefix=api_prefix)
app.include_router(public_signing.router, prefix=api_prefix)  # Public endpoints (no auth)

from fastapi.staticfiles import StaticFiles  # noqa: E402
import os  # noqa: E402

# serve static content (modules, PDFs, etc.)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)


@app.get("/")
def root():
    return {"status": "running"}
