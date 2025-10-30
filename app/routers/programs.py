from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.program import Program, Module

router = APIRouter(prefix="/programs", tags=["programs"])

@router.get("")
def list_programs(db: Session = Depends(get_db)):
    return db.query(Program).all()

@router.get("/{program_id}/modules")
def list_modules(program_id: str, db: Session = Depends(get_db)):
    return db.query(Module).filter(Module.program_id==program_id).all()
