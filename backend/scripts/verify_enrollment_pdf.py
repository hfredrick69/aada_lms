#!/usr/bin/env python3
"""
Verify that a generated enrollment PDF contains the expected form data values.

Usage:
    python backend/scripts/verify_enrollment_pdf.py --pdf path/to/file.pdf --data path/to/form.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, List

from pypdf import PdfReader


def extract_text(pdf_path: Path) -> str:
    reader = PdfReader(str(pdf_path))
    text_segments = []
    for page in reader.pages:
        text_segments.append(page.extract_text() or "")
    return "\n".join(text_segments)


def flatten_strings(payload: Any) -> List[str]:
    values: List[str] = []
    if isinstance(payload, dict):
        for value in payload.values():
            values.extend(flatten_strings(value))
    elif isinstance(payload, list):
        for item in payload:
            values.extend(flatten_strings(item))
    elif isinstance(payload, str):
        normalized = payload.strip()
        if normalized:
            values.append(normalized)
    return values


def main():
    parser = argparse.ArgumentParser(description="Verify enrollment agreement PDF content.")
    parser.add_argument("--pdf", required=True, help="Path to the generated PDF file.")
    parser.add_argument(
        "--data",
        required=True,
        help="Path to JSON file containing the form_data stored on SignedDocument.",
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    data_path = Path(args.data)

    if not pdf_path.exists():
        raise SystemExit(f"PDF not found: {pdf_path}")

    if not data_path.exists():
        raise SystemExit(f"Data file not found: {data_path}")

    pdf_text = extract_text(pdf_path).lower()
    with data_path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    strings = flatten_strings(data)
    missing = []
    for entry in strings:
        normalized = entry.lower()
        if len(normalized) < 3:
            continue
        if normalized not in pdf_text:
            missing.append(entry)

    if not missing:
        print("✅ PDF verification succeeded – all captured values were found.")
    else:
        print("⚠️ PDF verification found missing values:")
        for value in missing:
            print(f"  - {value}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
