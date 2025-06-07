"""Tests for the FileScanner utility."""

from pathlib import Path
import pytest

from src.utils.file_scanner import FileScanner


def test_scan_returns_audio_files(tmp_path):
    music_dir = tmp_path / "music"
    music_dir.mkdir()
    (music_dir / "song.mp3").write_bytes(b"data")
    (music_dir / "track.wav").write_bytes(b"data")
    (music_dir / "image.png").write_text("not audio")

    scanner = FileScanner()
    files = scanner.scan(str(music_dir))

    names = {p.name for p in files}
    assert names == {"song.mp3", "track.wav"}


def test_scan_invalid_folder():
    scanner = FileScanner()
    with pytest.raises(FileNotFoundError):
        scanner.scan("/non/existent/path")
