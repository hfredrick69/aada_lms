from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import models  # noqa: F401 ensure model registration
from app.routers import (
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
    complaints,
    credentials,
    transcripts,
    modules,
    h5p,
)

# Initialize DB tables (alembic will handle migrations; create_all is safe for first run)
# Base.metadata.create_all(bind=engine)

app = FastAPI(title="AADA LMS API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Admin Portal
        "http://127.0.0.1:5173",
        "http://localhost:5174",   # Student LMS Frontend
        "http://127.0.0.1:5174",
    ],
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
app.include_router(complaints.router, prefix=api_prefix)
app.include_router(credentials.router, prefix=api_prefix)
app.include_router(transcripts.router, prefix=api_prefix)
app.include_router(modules.router, prefix=api_prefix)
app.include_router(h5p.router, prefix=api_prefix)

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
