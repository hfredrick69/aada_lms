from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.enrollment import Enrollment

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("")
def list_enrollments(db: Session = Depends(get_db)):
    return db.query(Enrollment).all()
