from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class XapiStatementIn(BaseModel):
    actor: Dict[str, Any]
    verb: Dict[str, Any]
    object: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime


class XapiStatementOut(XapiStatementIn):
    id: UUID
    stored_at: datetime

    model_config = ConfigDict(from_attributes=True)
