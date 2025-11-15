"""
Enrollment agreement schema loader.

Exposes helper functions so both API endpoints and services can retrieve the
digitized enrollment agreement definition from a single JSON source.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict


SCHEMA_PATH = Path(__file__).with_name("enrollment_agreement_schema.json")


@lru_cache(maxsize=1)
def get_enrollment_agreement_schema() -> Dict[str, Any]:
    """
    Load and cache the enrollment agreement schema.

    Returns:
        Dict[str, Any]: Parsed schema dictionary.
    """
    with SCHEMA_PATH.open("r", encoding="utf-8") as schema_file:
        return json.load(schema_file)


def reload_enrollment_agreement_schema() -> None:
    """
    Clear the cached schema – useful for admin tasks that refresh the schema
    without restarting the process.
    """
    get_enrollment_agreement_schema.cache_clear()
