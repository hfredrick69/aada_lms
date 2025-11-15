"""
Advisor directory used for enrollment agreement workflows.
"""

from __future__ import annotations

from typing import List, Dict

ADVISOR_DIRECTORY: List[Dict[str, str]] = [
    {
        "id": "mary_jones",
        "name": "Mary Jones",
        "email": "mary.jones@aada.com",
        "title": "Admissions Advisor",
    },
    {
        "id": "charrease_fredrick",
        "name": "Charrease Fredrick",
        "email": "charrease@aada.com",
        "title": "Admissions Advisor",
    },
    {
        "id": "lee_parker",
        "name": "Lee Parker",
        "email": "lee.parker@aada.com",
        "title": "Enrollment Specialist",
    },
]


def list_advisors() -> List[Dict[str, str]]:
    """Return advisor directory entries."""
    return ADVISOR_DIRECTORY
