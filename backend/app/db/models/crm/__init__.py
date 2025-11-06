"""CRM Models - Lead Management System."""

from app.db.models.crm.lead import Lead, LeadSource, LeadCustomField
from app.db.models.crm.activity import Activity

__all__ = ["Lead", "LeadSource", "LeadCustomField", "Activity"]
