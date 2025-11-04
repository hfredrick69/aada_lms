from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import Text, cast
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models.xapi import XapiStatement
from app.schemas.xapi import XapiStatementIn, XapiStatementOut


router = APIRouter(prefix="/xapi", tags=["xAPI"])


@router.post("/statements", response_model=XapiStatementOut, status_code=status.HTTP_201_CREATED)
def create_xapi(statement: XapiStatementIn, db: Session = Depends(get_db)):
    rec = XapiStatement(actor=statement.actor, verb=statement.verb, object=statement.object,
                        result=statement.result, context=statement.context, timestamp=statement.timestamp)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


@router.get("/statements", response_model=List[XapiStatementOut])
def list_xapi_statements(
    agent: Optional[str] = Query(default=None, description="Filter by agent e-mail or name substring."),
    verb: Optional[str] = Query(default=None, description="Filter by verb id or display text."),
    since: Optional[datetime] = Query(default=None, description="Return statements stored since this timestamp."),
    limit: int = Query(default=200, le=1000, description="Maximum statements to return."),
    db: Session = Depends(get_db),
) -> List[XapiStatementOut]:
    query = db.query(XapiStatement)
    if agent:
        query = query.filter(cast(XapiStatement.actor, Text).ilike(f"%{agent}%"))
    if verb:
        query = query.filter(cast(XapiStatement.verb, Text).ilike(f"%{verb}%"))
    if since:
        query = query.filter(XapiStatement.timestamp >= since)
    records = (
        query.order_by(XapiStatement.timestamp.desc())
        .limit(limit)
        .all()
    )
    return records
