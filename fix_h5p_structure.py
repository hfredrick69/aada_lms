#!/usr/bin/env python3
import shutil
from pathlib import Path

# Path to extracted folder
extracted = Path("/Users/herbert/Projects/AADA/OnlineCourse/aada_lms/app/static/modules/module1/M1_H5P_HIPAAHotspot/extracted")
libraries_dir = extracted / "libraries"

print(f"Checking: {libraries_dir}")

if not libraries_dir.exists():
    print(f"libraries folder doesn't exist at {libraries_dir}")
    print(f"Contents of {extracted}:")
    for item in extracted.iterdir():
        print(f"  - {item.name}")
    exit(1)

print(f"\nMoving library folders from {libraries_dir} to {extracted}...")

# Move all H5P.* folders
moved_count = 0
for lib_folder in libraries_dir.glob("H5P.*"):
    if lib_folder.is_dir():
        dest = extracted / lib_folder.name
        print(f"Moving {lib_folder.name}...")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(lib_folder), str(dest))
        moved_count += 1

# Move other folders too
for lib_folder in libraries_dir.glob("*"):
    if lib_folder.is_dir() and not lib_folder.name.startswith("H5P."):
        dest = extracted / lib_folder.name
        print(f"Moving {lib_folder.name}...")
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(lib_folder), str(dest))
        moved_count += 1

print(f"\nMoved {moved_count} library folders")

# Remove empty libraries folder
if not any(libraries_dir.iterdir()):
    libraries_dir.rmdir()
    print("Removed empty libraries folder")

print(f"\nFinal structure of {extracted}:")
for item in sorted(extracted.iterdir()):
    print(f"  - {item.name}")
