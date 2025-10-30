from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.routers import auth, programs, enrollments, xapi, scorm, reports, attendance, skills, externships, finance, complaints, credentials, transcripts

# Initialize DB tables (alembic will handle migrations; create_all is safe for first run)
#Base.metadata.create_all(bind=engine)

app = FastAPI(title="AADA LMS API", version="1.0")

app.include_router(auth.router)
app.include_router(programs.router)
app.include_router(enrollments.router)
app.include_router(xapi.router)
app.include_router(scorm.router)
app.include_router(reports.router)
app.include_router(attendance.router)
app.include_router(skills.router)
app.include_router(externships.router)
app.include_router(finance.router)
app.include_router(complaints.router)
app.include_router(credentials.router)
app.include_router(transcripts.router)

from fastapi.staticfiles import StaticFiles
import os

# serve static content (modules, PDFs, etc.)
app.mount(
    "/static",
    StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")),
    name="static",
)

@app.get("/")
def root():
    return {"status": "running"}
