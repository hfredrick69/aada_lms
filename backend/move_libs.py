# flake8: noqa
import shutil
from pathlib import Path

extracted = Path("/Users/herbert/Projects/AADA/OnlineCourse/aada_lms/app/static/modules/module1/M1_H5P_HIPAAHotspot/extracted")
libraries_dir = extracted / "libraries"

if libraries_dir.exists():
    for item in libraries_dir.iterdir():
        if item.is_dir():
            dest = extracted / item.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.move(str(item), str(dest))
            print(f"Moved {item.name}")

    # Remove empty libraries folder
    libraries_dir.rmdir()
    print("Removed libraries folder")
else:
    print("libraries folder not found")

# List what's in extracted now
print("\nContents of extracted:")
for item in sorted(extracted.iterdir()):
    print(f"  {item.name}")
