#!/usr/bin/env python3
"""
H5P packager that copies dependencies from backend/app/static/h5p_libraries,
optionally running npm builds when a library ships without dist assets.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
LIBRARIES_ROOT = REPO_ROOT / "backend/app/static/h5p_libraries"
TMP_ROOT = REPO_ROOT / "tmp/h5p_build"
LIB_CACHE_ROOT = TMP_ROOT / "library_cache"
LIB_WORKSPACE_ROOT = TMP_ROOT / "library_workspaces"
NPM_CACHE_DIR = TMP_ROOT / ".npm_cache"


def ensure_dirs() -> None:
    for path in [TMP_ROOT, LIB_CACHE_ROOT, LIB_WORKSPACE_ROOT, NPM_CACHE_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def run(cmd: List[str], cwd: Path | None = None, env: Dict[str, str] | None = None) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env)
    if proc.returncode != 0:
        raise RuntimeError(f"Command {' '.join(cmd)} failed with {proc.returncode}")


def latest_mtime(path: Path) -> float:
    mtime = path.stat().st_mtime
    for child in path.rglob("*"):
        try:
            mtime = max(mtime, child.stat().st_mtime)
        except FileNotFoundError:
            continue
    return mtime


@dataclass(frozen=True)
class LibraryDescriptor:
    machine_name: str
    major: int
    minor: int

    @property
    def dir_name(self) -> str:
        return f"{self.machine_name}-{self.major}.{self.minor}"

    @property
    def source_path(self) -> Path:
        return LIBRARIES_ROOT / self.dir_name


def resolve_library(descriptor: LibraryDescriptor) -> Path:
    path = descriptor.source_path
    if not path.exists():
        raise FileNotFoundError(f"Missing library: {path}")
    return path


def maybe_build(descriptor: LibraryDescriptor) -> Path:
    cache_dir = LIB_CACHE_ROOT / descriptor.dir_name
    metadata = cache_dir / ".metadata.json"
    src = resolve_library(descriptor)
    src_mtime = latest_mtime(src)

    if cache_dir.exists():
        try:
            with metadata.open("r", encoding="utf-8") as fh:
                if json.load(fh).get("source_mtime") == src_mtime:
                    return cache_dir
        except Exception:
            shutil.rmtree(cache_dir)

    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    workspace = LIB_WORKSPACE_ROOT / descriptor.dir_name
    if workspace.exists():
        shutil.rmtree(workspace)
    shutil.copytree(src, workspace)

    package_json = workspace / "package.json"
    should_build = False
    if package_json.exists():
        with package_json.open("r", encoding="utf-8") as fh:
            pkg = json.load(fh)
        has_dist = any((workspace / candidate).exists() for candidate in ("dist", "build"))
        should_build = "build" in pkg.get("scripts", {}) and not has_dist

    npm_env = os.environ.copy()
    npm_env.setdefault("npm_config_cache", str(NPM_CACHE_DIR))

    if should_build:
        try:
            run(["npm", "install"], cwd=workspace, env=npm_env)
            run(["npm", "run", "build"], cwd=workspace, env=npm_env)
        except RuntimeError as exc:
            print(f"Warning: npm build failed for {descriptor.dir_name}: {exc}. Using existing sources.")
        finally:
            for node_dir in workspace.rglob("node_modules"):
                shutil.rmtree(node_dir, ignore_errors=True)

    shutil.copytree(workspace, cache_dir)
    shutil.rmtree(workspace, ignore_errors=True)

    with metadata.open("w", encoding="utf-8") as fh:
        json.dump({"source_mtime": src_mtime}, fh)

    return cache_dir


def gather_dependencies(initial: Iterable[LibraryDescriptor]) -> List[LibraryDescriptor]:
    queue = list(initial)
    seen: Set[Tuple[str, int, int]] = set()
    ordered: List[LibraryDescriptor] = []

    while queue:
        descriptor = queue.pop(0)
        key = (descriptor.machine_name, descriptor.major, descriptor.minor)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(descriptor)

        library_json = resolve_library(descriptor) / "library.json"
        if not library_json.exists():
            continue
        with library_json.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        for dep in data.get("preloadedDependencies", []):
            queue.append(LibraryDescriptor(dep["machineName"], dep["majorVersion"], dep["minorVersion"]))

    return ordered


def copy_libraries(libraries: List[LibraryDescriptor], target_root: Path) -> None:
    libs_dir = target_root / "libraries"
    libs_dir.mkdir(parents=True, exist_ok=True)
    for descriptor in libraries:
        cache_dir = maybe_build(descriptor)
        dest = libs_dir / descriptor.dir_name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(cache_dir, dest)


def load_manifest(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def package_activity(activity_id: str, source_dir: Path, output_path: Path) -> None:
    ensure_dirs()

    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")

    manifest_path = source_dir / "h5p.json"
    if not manifest_path.exists():
        raise FileNotFoundError(f"h5p.json missing in {source_dir}")

    manifest = load_manifest(manifest_path)
    dependencies = [
        LibraryDescriptor(dep["machineName"], dep["majorVersion"], dep["minorVersion"])
        for dep in manifest.get("preloadedDependencies", [])
    ]
    all_deps = gather_dependencies(dependencies)

    build_root = TMP_ROOT / f"{activity_id}_package"
    if build_root.exists():
        shutil.rmtree(build_root)
    build_root.mkdir(parents=True, exist_ok=True)

    shutil.copy(manifest_path, build_root / "h5p.json")
    content_dir = source_dir / "content"
    if content_dir.exists():
        shutil.copytree(content_dir, build_root / "content")

    copy_libraries(all_deps, build_root)

    for entry in source_dir.iterdir():
        if entry.name in {"content", "h5p.json"}:
            continue
        dest = build_root / entry.name
        if entry.is_dir():
            shutil.copytree(entry, dest)
        elif entry.is_file():
            shutil.copy(entry, dest)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists():
        output_path.unlink()

    from zipfile import ZipFile, ZIP_DEFLATED

    with ZipFile(output_path, "w", ZIP_DEFLATED) as zipf:
        for path in build_root.rglob("*"):
            if path.is_file():
                zipf.write(path, path.relative_to(build_root))

    print(f"Packaged {activity_id} -> {output_path}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="H5P packaging helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    package_parser = subparsers.add_parser("package", help="Create a .h5p package")
    package_parser.add_argument("--activity-id", required=True)
    package_parser.add_argument("--source", required=True)
    package_parser.add_argument("--output", required=True)

    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> None:
    args = parse_args(argv or sys.argv[1:])
    if args.command == "package":
        package_activity(args.activity_id, Path(args.source), Path(args.output))


if __name__ == "__main__":
    main()
