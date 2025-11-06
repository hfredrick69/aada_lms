"""add crm schema and tables for lead management

Revision ID: 0007_crm_schema
Revises: 0006_enable_encryption_infrastructure
Create Date: 2025-11-06 00:00:00.000000
"""
# flake8: noqa: E128, E501

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0007_crm_schema"
down_revision = "0006_enable_encryption_infrastructure"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create CRM schema
    op.execute("CREATE SCHEMA IF NOT EXISTS crm")

    # Create lead_sources table
    op.create_table(
        "lead_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(length=50), nullable=False, unique=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        schema="crm"
    )

    # Create leads table
    op.create_table(
        "leads",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("address_line1", sa.String(length=255), nullable=True),
        sa.Column("address_line2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("state", sa.String(length=2), nullable=True),
        sa.Column("zip_code", sa.String(length=10), nullable=True),
        sa.Column("lead_source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm.lead_sources.id"), nullable=False),
        sa.Column("lead_status", sa.String(length=50), nullable=False, server_default=sa.text("'new'")),
        sa.Column("lead_score", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("program_interest_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("programs.id"), nullable=True),
        sa.Column("converted_to_application_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        schema="crm"
    )

    # Create indexes for leads
    op.create_index("idx_leads_email", "leads", ["email"], schema="crm")
    op.create_index("idx_leads_status", "leads", ["lead_status"], schema="crm")
    op.create_index("idx_leads_assigned_to", "leads", ["assigned_to_id"], schema="crm")
    op.create_index("idx_leads_created_at", "leads", ["created_at"], schema="crm")

    # Create activities table
    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("entity_type", sa.String(length=50), nullable=False),  # lead, application, user
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("activity_type", sa.String(length=50), nullable=False),  # call, email, sms, meeting, note, task
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("due_date", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("completed_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("assigned_to_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_by_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        schema="crm"
    )

    # Create indexes for activities
    op.create_index("idx_activities_entity", "activities", ["entity_type", "entity_id"], schema="crm")
    op.create_index("idx_activities_assigned_to", "activities", ["assigned_to_id"], schema="crm")
    op.create_index("idx_activities_due_date", "activities", ["due_date"], schema="crm")

    # Create lead_custom_fields table
    op.create_table(
        "lead_custom_fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("crm.leads.id", ondelete="CASCADE"), nullable=False),
        sa.Column("field_name", sa.String(length=100), nullable=False),
        sa.Column("field_value", sa.Text, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        schema="crm"
    )

    # Create index for custom fields
    op.create_index("idx_lead_custom_fields_lead", "lead_custom_fields", ["lead_id"], schema="crm")

    # Insert default lead sources
    op.execute("""
        INSERT INTO crm.lead_sources (name, description) VALUES
        ('Website', 'Lead from website inquiry form'),
        ('Phone', 'Lead from phone inquiry'),
        ('Walk-In', 'Lead from walk-in visit'),
        ('Referral', 'Lead from student/staff referral'),
        ('Social Media', 'Lead from social media advertising'),
        ('Google Ads', 'Lead from Google advertising'),
        ('Career Fair', 'Lead from career fair'),
        ('Other', 'Other lead source')
    """)

    # Add new admissions roles
    op.execute("""
        INSERT INTO roles (id, name, description) VALUES
        (gen_random_uuid(), 'admissions_counselor', 'Admissions counselor - manage leads and applications'),
        (gen_random_uuid(), 'admissions_manager', 'Admissions manager - oversee admissions team and reporting')
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table("lead_custom_fields", schema="crm")
    op.drop_table("activities", schema="crm")
    op.drop_table("leads", schema="crm")
    op.drop_table("lead_sources", schema="crm")

    # Drop CRM schema
    op.execute("DROP SCHEMA IF EXISTS crm CASCADE")

    # Remove admissions roles
    op.execute("DELETE FROM roles WHERE name IN ('admissions_counselor', 'admissions_manager')")
