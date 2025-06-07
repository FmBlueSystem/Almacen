"""
Servicio para gestión de archivos de música
"""

import logging
from pathlib import Path
from typing import List

from ..models.song import Song, SongRepository
from ..database.connection import DatabaseConnection
from ..utils.file_scanner import FileScanner
from .metadata_extractor import MetadataExtractor

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
        self.scanner = FileScanner()
        self.metadata_extractor = MetadataExtractor()
        
    def import_folder(self, folder_path: str) -> tuple[int, int]:
        """
        Importar archivos de música desde una carpeta
        
        Args:
            folder_path: Ruta a la carpeta
            
        Returns:
            tuple[int, int]: (archivos importados, archivos fallidos)
        """
        imported = 0
        failed = 0

        try:
            files = self.scanner.scan(folder_path)
        except FileNotFoundError:
            raise

        for file_path in files:
            try:
                if not self.songs.exists(file_path):
                    song = self.metadata_extractor.extract(file_path)
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

            if path.suffix.lower() not in self.scanner.extensions:
                failed += 1
                logger.error(f"Formato no soportado: {file_path}")
                continue

            try:
                if not self.songs.exists(path):
                    song = self.metadata_extractor.extract(path)
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
