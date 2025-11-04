from fastapi import APIRouter


router = APIRouter(prefix="/scorm", tags=["scorm"])


@router.post("/records")
def upsert_record():
    return {"status": "ok"}
