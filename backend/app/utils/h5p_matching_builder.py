import csv
import io
import json
import re
import shutil
import tempfile
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

LIBRARY_ROOT = Path("app/static/h5p_libraries")
MAIN_LIBRARY = "H5P.Matching"
CHOICE_TYPES = {"text", "image"}

DEFAULT_L10N = {
    "checkAnswer": "Check",
    "showSolutionButton": "Show solution",
    "tryAgain": "Retry",
    "correct": "Correct!",
    "incorrect": "Incorrect!",
    "correctSolution": "Correct solution",
    "choiceUnMatched": "@title. Unmatched",
    "choiceMatched": "@title matched with @oppositeTitle",
    "choiceShouldBeMatched": "@title should have been matched with @oppositeTitle",
}

DEFAULT_BEHAVIOUR = {
    "enableRetry": True,
    "enableSolutionsButton": True,
    "passPercentage": 100,
}


class H5PGenerationError(Exception):
    """Raised when we cannot generate a valid H5P package."""


@dataclass(frozen=True)
class LibraryEntry:
    machine_name: str
    version: Tuple[int, int, int]
    path: Path
    metadata: Dict

    @property
    def folder_name(self) -> str:
        """Return directory name expected inside the H5P package."""
        major, minor, _ = self.version
        return f"{self.machine_name}-{major}.{minor}"


def _load_library_entry(path: Path) -> Optional[LibraryEntry]:
    library_json = path / "library.json"
    if not library_json.exists():
        return None
    try:
        metadata = json.loads(library_json.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise H5PGenerationError(f"Malformed library.json in {path}: {exc}") from exc

    machine = metadata.get("machineName")
    if not machine:
        return None

    version = (
        int(metadata.get("majorVersion", 0)),
        int(metadata.get("minorVersion", 0)),
        int(metadata.get("patchVersion", 0)),
    )
    return LibraryEntry(machine_name=machine, version=version, path=path, metadata=metadata)


@lru_cache(maxsize=1)
def _library_index() -> Dict[str, List[LibraryEntry]]:
    """Index available libraries by machineName."""
    if not LIBRARY_ROOT.exists():
        raise H5PGenerationError(
            f"Library root {LIBRARY_ROOT} is missing. Download H5P libraries first."
        )

    index: Dict[str, List[LibraryEntry]] = {}
    for child in LIBRARY_ROOT.iterdir():
        if not child.is_dir():
            continue
        entry = _load_library_entry(child)
        if not entry:
            continue
        index.setdefault(entry.machine_name, []).append(entry)

    for entries in index.values():
        entries.sort(key=lambda e: e.version, reverse=True)
    return index


def _select_library(machine: str, major: int, minor: int) -> LibraryEntry:
    entries = _library_index().get(machine, [])
    for entry in entries:
        entry_major, entry_minor, _ = entry.version
        if entry_major == major and entry_minor == minor:
            return entry
    raise H5PGenerationError(
        f"Required library {machine} {major}.{minor} not found in {LIBRARY_ROOT}."
    )


def _ensure_assets_exist(entry: LibraryEntry) -> None:
    """Validate that preloaded assets referenced in library.json exist on disk."""
    base = entry.path
    missing: List[str] = []

    for asset in entry.metadata.get("preloadedJs", []):
        asset_path = base / asset["path"]
        if not asset_path.exists():
            missing.append(str(asset_path.relative_to(base)))

    for asset in entry.metadata.get("preloadedCss", []):
        asset_path = base / asset["path"]
        if not asset_path.exists():
            missing.append(str(asset_path.relative_to(base)))

    if missing:
        joined = ", ".join(missing)
        raise H5PGenerationError(
            f"Library {entry.machine_name} is missing built assets ({joined}). "
            "Run `npm install && npm run build` in the library directory to compile them."
        )


def _collect_library_tree(
    machine: str, major: int, minor: int, visited: Optional[set] = None
) -> List[LibraryEntry]:
    if visited is None:
        visited = set()
    key = (machine, major, minor)
    if key in visited:
        return []
    visited.add(key)

    entry = _select_library(machine, major, minor)
    _ensure_assets_exist(entry)

    dependencies: List[LibraryEntry] = []
    for dep in entry.metadata.get("preloadedDependencies", []):
        dependencies.extend(
            _collect_library_tree(dep["machineName"], dep["majorVersion"], dep["minorVersion"], visited)
        )

    return [entry] + dependencies


def _copy_library(entry: LibraryEntry, target_root: Path) -> None:
    dest = target_root / entry.folder_name
    if dest.exists():
        shutil.rmtree(dest)

    ignore_patterns = shutil.ignore_patterns(
        "node_modules",
        ".git",
        ".github",
        "tests",
        "test",
        "cypress",
        "tmp",
        "*.log",
    )
    shutil.copytree(entry.path, dest, ignore=ignore_patterns)


def generate_matching_h5p(
    *,
    title: str,
    pairs: Sequence[Tuple[str, str]],
    choice_type: str = "text",
    description: Optional[str] = None,
) -> Tuple[bytes, str]:
    """Build an H5P package for H5P.Matching and return (bytes, safe_filename)."""
    cleaned_pairs = [
        (term.strip(), definition.strip())
        for term, definition in pairs
        if term.strip() and definition.strip()
    ]

    if len(cleaned_pairs) < 2:
        raise H5PGenerationError("Provide at least two term/definition pairs.")

    if choice_type not in CHOICE_TYPES:
        raise H5PGenerationError(
            f"Invalid choice type '{choice_type}'. Allowed values: {', '.join(sorted(CHOICE_TYPES))}."
        )

    title = title.strip() or "Matching Exercise"

    main_library = _select_library(MAIN_LIBRARY, 1, 0)
    dependency_entries = _collect_library_tree(MAIN_LIBRARY, 1, 0)

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_root = Path(tmp_dir)
        content_dir = tmp_root / "content"
        content_dir.mkdir()

        content_json = {
            "choiceType": choice_type,
            "title": description.strip() if description else title,
            "pairs": [{"source": term, "target": definition} for term, definition in cleaned_pairs],
            "l10n": DEFAULT_L10N,
            "behaviour": DEFAULT_BEHAVIOUR,
        }
        (content_dir / "content.json").write_text(
            json.dumps(content_json, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        preloaded_dependencies = [
            {
                "machineName": MAIN_LIBRARY,
                "majorVersion": main_library.version[0],
                "minorVersion": main_library.version[1],
            }
        ]

        seen = {(MAIN_LIBRARY, main_library.version[0], main_library.version[1])}
        for entry in dependency_entries[1:]:
            key = (entry.machine_name, entry.version[0], entry.version[1])
            if key in seen:
                continue
            preloaded_dependencies.append(
                {
                    "machineName": entry.machine_name,
                    "majorVersion": entry.version[0],
                    "minorVersion": entry.version[1],
                }
            )
            seen.add(key)

        h5p_json = {
            "title": title,
            "language": "en",
            "mainLibrary": MAIN_LIBRARY,
            "embedTypes": ["iframe"],
            "license": "U",
            "preloadedDependencies": preloaded_dependencies,
        }

        (tmp_root / "h5p.json").write_text(
            json.dumps(h5p_json, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        libs_dir = tmp_root / "libraries"
        libs_dir.mkdir()
        for entry in dependency_entries:
            _copy_library(entry, libs_dir)

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for path in tmp_root.rglob("*"):
                if path.is_dir():
                    continue
                zf.write(path, path.relative_to(tmp_root).as_posix())

        buffer.seek(0)
        safe_title = _slugify(title) or "matching"
        filename = f"{safe_title}.h5p"
        return buffer.read(), filename


def parse_pairs_from_table(raw: str) -> List[Tuple[str, str]]:
    """Parse a loosely formatted table into term/definition pairs."""
    if not raw or not raw.strip():
        raise H5PGenerationError("Provide at least two rows with term and definition.")

    lines = [line.strip() for line in raw.strip().splitlines() if line.strip()]
    if not lines:
        raise H5PGenerationError("Provide at least two rows with term and definition.")

    cleaned_lines = _strip_markdown_header(lines)
    rows: List[Tuple[str, str]] = []

    if not cleaned_lines:
        raise H5PGenerationError("No data rows detected.")

    uses_tabs = any("\t" in line for line in cleaned_lines)

    for line in cleaned_lines:
        if line.startswith("|") and line.endswith("|"):
            parts = [part.strip() for part in line.strip("|").split("|")]
        elif "|" in line:
            parts = [part.strip() for part in line.split("|")]
        else:
            reader = csv.reader(io.StringIO(line), delimiter="\t" if uses_tabs else ",", skipinitialspace=True)
            row = next(reader, [])
            parts = [cell.strip() for cell in row]

        parts = [part for part in parts if part]
        if len(parts) < 2:
            continue
        rows.append((parts[0], parts[1]))

    if len(rows) < 2:
        raise H5PGenerationError("Provide at least two valid rows.")
    return rows


def _strip_markdown_header(lines: Sequence[str]) -> List[str]:
    if not lines:
        return []
    output: List[str] = list(lines)
    header_tokens = {"term", "definition", "terms", "definitions"}
    first_tokens = {token.strip().lower() for token in re.split(r"[|\t,]", output[0]) if token.strip()}
    if header_tokens & first_tokens:
        output = output[1:]
        if output and all(ch in "|-: " for ch in output[0]):
            output = output[1:]
    return output


def _slugify(value: str) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")
