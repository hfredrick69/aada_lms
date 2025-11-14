"""
Regenerate signed PDF artifacts for historical documents.

Usage examples:
    # Preview which completed agreements will be regenerated
    DATABASE_URL=postgresql+psycopg2://... PYTHONPATH=backend \\
        python backend/scripts/regen_signed_pdfs.py --dry-run

    # Force regeneration for a specific agreement
    DATABASE_URL=postgresql+psycopg2://... PYTHONPATH=backend \\
        python backend/scripts/regen_signed_pdfs.py --document-id <uuid> --rebuild-existing
"""

from __future__ import annotations

import argparse
from typing import Iterable, List, Tuple
import uuid

from sqlalchemy import or_

from app.db.session import SessionLocal
from app.db.models.document import DocumentTemplate, SignedDocument
from app.routers.documents import _generate_signed_pdf


def _collect_documents(
    session,
    document_ids: Iterable[uuid.UUID] | None,
    rebuild_existing: bool,
    limit: int | None,
) -> List[SignedDocument]:
    """Fetch documents that match the provided filters."""
    query = session.query(SignedDocument).filter(SignedDocument.status == "completed")

    if document_ids:
        query = query.filter(SignedDocument.id.in_(list(document_ids)))

    if not rebuild_existing:
        query = query.filter(
            or_(SignedDocument.signed_file_path.is_(None), SignedDocument.signed_file_path == "")
        )

    query = query.order_by(SignedDocument.completed_at.asc())

    documents: List[SignedDocument] = query.all()
    if limit is not None and limit >= 0:
        documents = documents[:limit]

    return documents


def regenerate_signed_pdfs(
    session,
    documents: Iterable[SignedDocument],
    dry_run: bool,
) -> Tuple[int, int, List[Tuple[uuid.UUID, str]]]:
    """
    Regenerate PDFs for the provided documents.

    Returns:
        (processed_count, success_count, failures)
    """
    processed = 0
    success = 0
    failures: List[Tuple[uuid.UUID, str]] = []

    for doc in documents:
        processed += 1

        template = session.query(DocumentTemplate).filter(DocumentTemplate.id == doc.template_id).first()
        if not template:
            failures.append((doc.id, "missing_template"))
            continue

        if dry_run:
            print(
                f"[DRY-RUN] Would regenerate document {doc.id} using template "
                f"'{template.name}' v{template.version}."
            )
            continue

        regenerated = _generate_signed_pdf(doc, template, session, current_user=None, request=None)
        if regenerated:
            session.refresh(doc)
            success += 1
        else:
            failures.append((doc.id, "generation_failed"))

    return processed, success, failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Regenerate final signed PDFs for completed agreements.")
    parser.add_argument(
        "--document-id",
        action="append",
        type=uuid.UUID,
        help="Specific document ID to regenerate (can be provided multiple times).",
    )
    parser.add_argument(
        "--rebuild-existing",
        action="store_true",
        help="Regenerate even if signed_file_path already exists.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit the number of documents to process (useful for testing).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching documents without writing files.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    session = SessionLocal()
    try:
        documents = _collect_documents(session, args.document_id, args.rebuild_existing, args.limit)

        if not documents:
            print("No documents matched the provided filters.")
            return

        print(f"Found {len(documents)} completed document(s) to process.")
        processed, regenerated, failures = regenerate_signed_pdfs(session, documents, args.dry_run)

        if args.dry_run:
            print("Dry-run complete; no PDFs were regenerated.")
        else:
            print(f"Regenerated {regenerated} of {processed} documents.")

        if failures:
            print("Failures:")
            for doc_id, reason in failures:
                print(f"  - {doc_id}: {reason}")
    finally:
        session.close()


if __name__ == "__main__":
    main()
