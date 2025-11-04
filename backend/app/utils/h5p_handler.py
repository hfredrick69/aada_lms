"""
H5P Content Handler
Extracts and serves H5P packages (.h5p files) for the LMS
"""
import zipfile
import json
import shutil
from pathlib import Path
from typing import Dict, Optional
import hashlib


class H5PHandler:
    def __init__(self, h5p_storage_path: Path, cache_path: Path):
        """
        Initialize H5P handler

        Args:
            h5p_storage_path: Base path where .h5p files are stored
            cache_path: Path where extracted H5P content is cached
        """
        self.h5p_storage_path = Path(h5p_storage_path)
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)

    def get_h5p_path(self, activity_id: str) -> Optional[Path]:
        """Find the .h5p file for a given activity ID"""
        # Search in module directories - try multiple patterns
        search_patterns = [
            self.h5p_storage_path / f"**/{activity_id}.h5p",
            self.h5p_storage_path / f"**/{activity_id}/**/*.h5p",
        ]

        for pattern in search_patterns:
            matches = list(self.h5p_storage_path.glob(str(pattern.relative_to(self.h5p_storage_path))))
            if matches:
                # Filter out content_only files, prefer others
                non_content_only = [m for m in matches if 'content_only' not in m.name.lower()]
                if non_content_only:
                    return non_content_only[0]
                return matches[0]

        return None

    def get_cache_key(self, h5p_file: Path) -> str:
        """Generate cache key based on file path and modification time"""
        stat = h5p_file.stat()
        key_string = f"{h5p_file}_{stat.st_mtime}_{stat.st_size}"
        return hashlib.md5(key_string.encode()).hexdigest()

    def extract_h5p(self, activity_id: str, force_refresh: bool = False) -> Optional[Path]:
        """
        Extract H5P file to cache directory

        Args:
            activity_id: H5P activity identifier
            force_refresh: Force re-extraction even if cached

        Returns:
            Path to extracted content directory, or None if not found
        """
        h5p_file = self.get_h5p_path(activity_id)
        if not h5p_file or not h5p_file.exists():
            return None

        # Check cache
        cache_key = self.get_cache_key(h5p_file)
        cache_dir = self.cache_path / cache_key

        if cache_dir.exists() and not force_refresh:
            return cache_dir

        # Extract H5P file (it's a zip file)
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(h5p_file, "r") as zip_ref:
                zip_ref.extractall(cache_dir)

            # Ensure libraries are accessible at the cache root since the H5P
            # standalone player expects to load `/content/<library>/library.json`.
            libraries_dir = cache_dir / "libraries"
            if libraries_dir.exists() and libraries_dir.is_dir():
                for lib_folder in libraries_dir.iterdir():
                    if lib_folder.is_dir():
                        dest = cache_dir / lib_folder.name
                        if dest.exists():
                            shutil.rmtree(dest)
                        shutil.move(str(lib_folder), str(dest))

                # Remove empty libraries directory after moving contents.
                if not any(libraries_dir.iterdir()):
                    libraries_dir.rmdir()

            return cache_dir

        except Exception as e:
            print(f"Error extracting H5P file {h5p_file}: {e}")
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
            return None

    def get_h5p_json(self, activity_id: str) -> Optional[Dict]:
        """Get h5p.json metadata for an activity"""
        cache_dir = self.extract_h5p(activity_id)
        if not cache_dir:
            return None

        h5p_json_path = cache_dir / "h5p.json"
        if not h5p_json_path.exists():
            return None

        try:
            with open(h5p_json_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading h5p.json: {e}")
            return None

    def get_content_path(self, activity_id: str) -> Optional[Path]:
        """Get path to extracted content directory"""
        return self.extract_h5p(activity_id)
