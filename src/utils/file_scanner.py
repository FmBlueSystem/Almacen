"""Utility class for scanning directories recursively to find audio files."""

from pathlib import Path
from typing import List, Iterable


class FileScanner:
    """Recursively scan folders for supported audio files."""

    DEFAULT_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a"}

    def __init__(self, extensions: Iterable[str] | None = None) -> None:
        self.extensions = set(e.lower() for e in (extensions or self.DEFAULT_EXTENSIONS))

    def scan(self, folder: str) -> List[Path]:
        """Return a list of audio files found within ``folder``."""
        root = Path(folder)
        if not root.exists():
            raise FileNotFoundError(f"Folder not found: {folder}")

        files: List[Path] = []
        for path in root.rglob("*"):
            if path.suffix.lower() in self.extensions:
                files.append(path)
        return files
