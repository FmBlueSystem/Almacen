"""
Servicio para gestión de archivos de música
"""

import os
import logging
from pathlib import Path
from typing import List, Optional
from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3

from ..models.song import Song, SongRepository
from ..database.connection import DatabaseConnection

logger = logging.getLogger(__name__)

class MusicService:
    """Servicio para operaciones con archivos de música"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """
        Inicializar servicio
        
        Args:
            db_connection: Conexión a base de datos
        """
        self.songs = SongRepository(db_connection)
        
    def import_folder(self, folder_path: str) -> tuple[int, int]:
        """
        Importar archivos de música desde una carpeta
        
        Args:
            folder_path: Ruta a la carpeta
            
        Returns:
            tuple[int, int]: (archivos importados, archivos fallidos)
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise FileNotFoundError(f"Carpeta no encontrada: {folder_path}")
            
        imported = 0
        failed = 0
        
        for file_path in folder.rglob("*"):
            if file_path.suffix.lower() in [".mp3", ".wav", ".flac", ".m4a"]:
                try:
                    if not self.songs.exists(file_path):
                        song = self._extract_metadata(file_path)
                        if song:
                            self.songs.add(song)
                            imported += 1
                            logger.info(f"Importado: {file_path.name}")
                        else:
                            failed += 1
                            logger.warning(f"Sin metadatos: {file_path.name}")
                except Exception as e:
                    failed += 1
                    logger.error(f"Error importando {file_path.name}: {e}")
        
        return imported, failed
    
    def import_files(self, file_paths: List[str]) -> tuple[int, int]:
        """
        Importar archivos de música específicos
        
        Args:
            file_paths: Lista de rutas de archivos
            
        Returns:
            tuple[int, int]: (archivos importados, archivos fallidos)
        """
        imported = 0
        failed = 0
        
        for file_path in file_paths:
            path = Path(file_path)
            if not path.exists():
                failed += 1
                logger.error(f"Archivo no encontrado: {file_path}")
                continue
                
            try:
                if not self.songs.exists(path):
                    song = self._extract_metadata(path)
                    if song:
                        self.songs.add(song)
                        imported += 1
                        logger.info(f"Importado: {path.name}")
                    else:
                        failed += 1
                        logger.warning(f"Sin metadatos: {path.name}")
            except Exception as e:
                failed += 1
                logger.error(f"Error importando {path.name}: {e}")
        
        return imported, failed
    
    def _extract_metadata(self, file_path: Path) -> Optional[Song]:
        """
        Extraer metadatos de un archivo de música
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Optional[Song]: Canción con metadatos o None si no se pueden extraer
        """
        try:
            audio = MutagenFile(file_path, easy=True)
            if audio is None:
                return None
            
            if isinstance(audio, EasyID3):
                # MP3 con tags ID3
                title = audio.get("title", [""])[0] or file_path.stem
                artist = audio.get("artist", ["Desconocido"])[0]
                album = audio.get("album", [""])[0] or "Sin álbum"
                genre = audio.get("genre", [""])[0] or "Sin género"
                bpm = None
                if "bpm" in audio:
                    try:
                        bpm = int(float(audio["bpm"][0]))
                    except (ValueError, IndexError):
                        pass
            else:
                # Otros formatos
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
                    # Sin tags, usar nombre de archivo
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
                file_path=file_path
            )
            
        except Exception as e:
            logger.error(f"Error extrayendo metadatos de {file_path.name}: {e}")
            return None
    
    def search_songs(self, 
                    title: str = "", 
                    artist: str = "", 
                    genre: str = "",
                    page: int = 1,
                    per_page: int = 50) -> tuple[List[Song], int]:
        """
        Buscar canciones con filtros
        
        Args:
            title: Filtro por título
            artist: Filtro por artista
            genre: Filtro por género
            page: Número de página actual
            per_page: Canciones por página
            
        Returns:
            tuple[List[Song], int]: Lista de canciones que coinciden con el filtro y el número total de canciones que coinciden.
        """
        songs, total_items_matching_filter = self.songs.search(title, artist, genre, page, per_page)
        return songs, total_items_matching_filter
    
    def get_songs(self, page: int = 1, per_page: int = 50) -> tuple[List[Song], int]:
        """
        Obtener lista paginada de canciones
        
        Args:
            page: Número de página actual
            per_page: Canciones por página
            
        Returns:
            tuple[List[Song], int]: Lista de canciones y total de páginas
        """
        songs = self.songs.get_all(page, per_page)
        total_pages = self.songs.get_total_pages(per_page)
        return songs, total_pages

    def get_distinct_artists(self) -> List[str]:
        """Obtener lista de artistas distintos para filtros."""
        return self.songs.get_distinct_artists()

    def get_distinct_genres(self) -> List[str]:
        """Obtener lista de géneros distintos para filtros."""
        return self.songs.get_distinct_genres()

    def get_total_songs_count(self) -> int:
        """Obtener el número total de canciones."""
        return self.songs.get_total_songs_count()
