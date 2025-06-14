"""Utility class to extract audio metadata using mutagen."""

from pathlib import Path
from typing import Optional

from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.mp4 import MP4

from ..models.song import Song


class MetadataExtractor:
    """Extract metadata from audio files and return :class:`Song` objects."""

    def extract(self, file_path: Path) -> Optional[Song]:
        """Return a Song with metadata from ``file_path`` or ``None`` if not found."""
        try:
            audio = MutagenFile(file_path)
            if audio is None:
                return None

            title = file_path.stem
            artist = "Desconocido"
            album = "Sin álbum"
            genre = "Sin género"
            bpm = None

            # Special handling for MP4/M4A files
            if isinstance(audio, MP4):
                tags = audio.tags or {}
                title = tags.get("\xa9nam", [file_path.stem])[0]
                artist = tags.get("\xa9ART", ["Desconocido"])[0]
                album = tags.get("\xa9alb", ["Sin álbum"])[0]
                genre = tags.get("\xa9gen", ["Sin género"])[0]

                if "tmpo" in tags:
                    try:
                        bpm = int(tags["tmpo"][0])
                    except (ValueError, IndexError, TypeError):
                        bpm = None
                elif "----:com.apple.iTunes:BPM" in tags:
                    try:
                        raw = tags["----:com.apple.iTunes:BPM"][0]
                        if isinstance(raw, bytes):
                            raw = raw.decode("utf-8", "ignore")
                        bpm = int(raw)
                    except (ValueError, IndexError, TypeError):
                        bpm = None
            else:
                easy = MutagenFile(file_path, easy=True)
                if easy is not None and isinstance(getattr(easy, "tags", None), EasyID3):
                    title = easy.tags.get("title", [file_path.stem])[0] or file_path.stem
                    artist = easy.tags.get("artist", ["Desconocido"])[0]
                    album = easy.tags.get("album", ["Sin álbum"])[0]
                    genre = easy.tags.get("genre", ["Sin género"])[0]
                    if "bpm" in easy.tags:
                        try:
                            bpm = int(float(easy.tags["bpm"][0]))
                        except (ValueError, IndexError):
                            bpm = None
                elif audio.tags:
                    tags = audio.tags
                    title = str(tags.get("title", [file_path.stem])[0])
                    artist = str(tags.get("artist", ["Desconocido"])[0])
                    album = str(tags.get("album", ["Sin álbum"])[0])
                    genre = str(tags.get("genre", ["Sin género"])[0])
                    if "bpm" in tags:
                        try:
                            bpm = int(float(str(tags["bpm"][0])))
                        except (ValueError, IndexError):
                            bpm = None

            return Song(
                id=None,
                title=title,
                artist=artist,
                album=album,
                genre=genre,
                bpm=bpm,
                file_path=file_path,
            )
        except Exception:
            return None
