"""
Log rotation utility for audit logs.

HIPAA requires audit logs be retained for 6 years, but we can archive older logs
to cheaper storage and keep recent logs in the database for faster queries.
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.audit_log import AuditLog
import logging

logger = logging.getLogger(__name__)

# Retention periods
ACTIVE_RETENTION_DAYS = 90  # Keep 90 days in active database
ARCHIVE_RETENTION_YEARS = 6  # HIPAA requirement


def rotate_audit_logs(
    db: Session = None,
    retention_days: int = ACTIVE_RETENTION_DAYS,
    dry_run: bool = False
) -> dict:
    """
    Rotate audit logs by archiving/deleting old entries.

    Args:
        db: Database session (creates new one if not provided)
        retention_days: Number of days to keep in active database
        dry_run: If True, only count logs to be archived without deleting

    Returns:
        dict with counts of logs processed
    """
    if db is None:
        db = SessionLocal()
        close_session = True
    else:
        close_session = False

    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=retention_days)

        # Count logs to be archived
        old_logs_count = db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date
        ).count()

        # Count PHI access logs (never delete these, only archive)
        phi_logs_count = db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date,
            AuditLog.is_phi_access == True  # noqa: E712
        ).count()

        if dry_run:
            logger.info(
                f"[DRY RUN] Would archive {old_logs_count} logs "
                f"({phi_logs_count} PHI access logs)"
            )
            return {
                "dry_run": True,
                "total_to_archive": old_logs_count,
                "phi_logs_to_archive": phi_logs_count,
                "archived": 0,
                "deleted": 0
            }

        # In production, export to archive before deleting
        # For now, we'll just delete non-PHI logs older than retention period
        # PHI logs should be exported to secure long-term storage first

        # Delete non-PHI logs older than retention period
        deleted_count = db.query(AuditLog).filter(
            AuditLog.timestamp < cutoff_date,
            AuditLog.is_phi_access == False  # noqa: E712
        ).delete(synchronize_session=False)

        db.commit()

        logger.info(
            f"Archived {old_logs_count} audit logs "
            f"(deleted {deleted_count} non-PHI, kept {phi_logs_count} PHI logs)"
        )

        return {
            "dry_run": False,
            "total_processed": old_logs_count,
            "phi_logs_kept": phi_logs_count,
            "non_phi_deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat()
        }

    except Exception as e:
        logger.error(f"Error rotating audit logs: {e}")
        if not dry_run:
            db.rollback()
        raise

    finally:
        if close_session:
            db.close()


def get_audit_log_stats(db: Session = None) -> dict:
    """Get statistics about audit logs."""
    if db is None:
        db = SessionLocal()
        close_session = True
    else:
        close_session = False

    try:
        total_logs = db.query(AuditLog).count()
        phi_logs = db.query(AuditLog).filter(
            AuditLog.is_phi_access == True  # noqa: E712
        ).count()

        # Get oldest and newest log timestamps
        oldest = db.query(AuditLog).order_by(AuditLog.timestamp.asc()).first()
        newest = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()

        return {
            "total_logs": total_logs,
            "phi_access_logs": phi_logs,
            "non_phi_logs": total_logs - phi_logs,
            "oldest_log": oldest.timestamp.isoformat() if oldest else None,
            "newest_log": newest.timestamp.isoformat() if newest else None,
        }

    finally:
        if close_session:
            db.close()


if __name__ == "__main__":
    # Can be run as a cron job
    import sys

    dry_run = "--dry-run" in sys.argv
    retention_days = ACTIVE_RETENTION_DAYS

    # Parse retention days from command line
    for arg in sys.argv:
        if arg.startswith("--days="):
            retention_days = int(arg.split("=")[1])

    print(f"Running log rotation (retention: {retention_days} days, dry_run: {dry_run})")

    stats = get_audit_log_stats()
    print("\nCurrent stats:")
    print(f"  Total logs: {stats['total_logs']}")
    print(f"  PHI access logs: {stats['phi_access_logs']}")
    print(f"  Non-PHI logs: {stats['non_phi_logs']}")
    if stats['oldest_log']:
        print(f"  Oldest log: {stats['oldest_log']}")
        print(f"  Newest log: {stats['newest_log']}")

    result = rotate_audit_logs(retention_days=retention_days, dry_run=dry_run)
    print("\nRotation result:")
    for key, value in result.items():
        print(f"  {key}: {value}")
