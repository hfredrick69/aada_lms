"""
Utility script to reset enrollment agreement statuses for testing demos.

Usage:
    PYTHONPATH=backend python backend/scripts/reset_agreement_statuses.py --keep-completed 5

The script converts every signed document (except the newest `keep_completed`)
back to the `student_signed` state so the admin portal shows "Awaiting counter-sign".
"""

from __future__ import annotations

import argparse
from typing import Sequence

from app.db.session import SessionLocal
from app.db.models.document import SignedDocument


def reset_statuses(keep_completed: int) -> tuple[int, int]:
    """
    Reset document statuses while leaving the newest `keep_completed` untouched.

    Returns:
        tuple[int, int]: (total_documents, reset_count)
    """
    session = SessionLocal()
    try:
        documents: Sequence[SignedDocument] = (
            session.query(SignedDocument)
            .order_by(SignedDocument.created_at.desc())
            .all()
        )

        total = len(documents)
        if total <= keep_completed:
            return total, 0

        reset_docs = documents[keep_completed:]
        for doc in reset_docs:
            doc.status = "student_signed"
            doc.counter_signed_at = None
            doc.completed_at = None
            doc.signed_file_path = None

        session.commit()
        return total, len(reset_docs)
    finally:
        session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Reset agreement statuses to 'Awaiting counter-sign'.")
    parser.add_argument(
        "--keep-completed",
        type=int,
        default=5,
        help="Number of most-recent documents to keep as completed (default: 5).",
    )
    args = parser.parse_args()

    total, reset_count = reset_statuses(max(args.keep_completed, 0))
    print(f"Processed {total} documents; reset {reset_count} to 'student_signed'.")


if __name__ == "__main__":
    main()
