"""Utility class to extract audio metadata using mutagen."""

from pathlib import Path
from typing import Optional

from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3

from ..models.song import Song


class MetadataExtractor:
    """Extract metadata from audio files and return :class:`Song` objects."""

    def extract(self, file_path: Path) -> Optional[Song]:
        """Return a Song with metadata from ``file_path`` or ``None`` if not found."""
        try:
            audio = MutagenFile(file_path, easy=True)
            if audio is None:
                return None

            if isinstance(audio, EasyID3):
                title = audio.get("title", [file_path.stem])[0] or file_path.stem
                artist = audio.get("artist", ["Desconocido"])[0]
                album = audio.get("album", ["Sin álbum"])[0]
                genre = audio.get("genre", ["Sin género"])[0]
                bpm = None
                if "bpm" in audio:
                    try:
                        bpm = int(float(audio["bpm"][0]))
                    except (ValueError, IndexError):
                        pass
            else:
                tags = audio.tags
                if tags:
                    title = str(tags.get("title", [file_path.stem])[0])
                    artist = str(tags.get("artist", ["Desconocido"])[0])
                    album = str(tags.get("album", ["Sin álbum"])[0])
                    genre = str(tags.get("genre", ["Sin género"])[0])
                    bpm = None
                    if "bpm" in tags:
                        try:
                            bpm = int(float(str(tags["bpm"][0])))
                        except (ValueError, IndexError):
                            pass
                else:
                    title = file_path.stem
                    artist = "Desconocido"
                    album = "Sin álbum"
                    genre = "Sin género"
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
