#!/usr/bin/env python3
import zipfile
import os
import shutil
from pathlib import Path

# Paths
h5p_file = Path("app/static/modules/module1/M1_H5P_EthicsBranching.h5p")
target_dir = Path("app/static/modules/module1/M1_H5P_EthicsBranching/extracted")

print(f"Extracting {h5p_file} to {target_dir}")

# Remove old extracted directory if exists
if target_dir.exists():
    shutil.rmtree(target_dir)

# Create new extracted directory
target_dir.mkdir(parents=True, exist_ok=True)

# Extract the h5p file
with zipfile.ZipFile(h5p_file, 'r') as zip_ref:
    zip_ref.extractall(target_dir)

print(f"\nExtraction complete. Contents:")
for item in sorted(target_dir.iterdir()):
    print(f"  - {item.name}")

# Check if libraries subfolder exists and move contents to root
libraries_dir = target_dir / "libraries"
if libraries_dir.exists() and libraries_dir.is_dir():
    print(f"\nMoving libraries from {libraries_dir} to {target_dir}...")

    moved_count = 0
    for lib_folder in libraries_dir.iterdir():
        if lib_folder.is_dir():
            dest = target_dir / lib_folder.name
            print(f"  Moving {lib_folder.name}...")
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(str(lib_folder), str(dest))
            moved_count += 1

    print(f"\nMoved {moved_count} library folders")

    # Remove empty libraries folder
    if not any(libraries_dir.iterdir()):
        libraries_dir.rmdir()
        print("Removed empty libraries folder")

print(f"\nFinal structure:")
for item in sorted(target_dir.iterdir()):
    print(f"  - {item.name}")

print("\nDone!")
