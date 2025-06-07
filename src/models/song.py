"""
Modelo para la gestión de canciones
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Tuple

@dataclass
class Song:
    """Modelo de datos para una canción"""
    id: Optional[int]
    title: str
    artist: str
    album: str
    genre: str
    bpm: Optional[int]
    file_path: Path

    @classmethod
    def from_db_row(cls, row):
        """Crear instancia desde una fila de base de datos"""
        return cls(
            id=row["id"],
            title=row["title"],
            artist=row["artist"],
            album=row["album"],
            genre=row["genre"],
            bpm=row["bpm"],
            file_path=Path(row["file_path"])
        )

class SongRepository:
    """Repositorio para operaciones CRUD de canciones"""
    
    def __init__(self, db_connection):
        """
        Inicializar repositorio
        
        Args:
            db_connection: Instancia de DatabaseConnection
        """
        self.db = db_connection
        
    def get_all(self, page: int = 1, per_page: int = 50) -> list[Song]:
        """
        Obtener canciones paginadas
        
        Args:
            page: Número de página (comienza en 1)
            per_page: Canciones por página
            
        Returns:
            list[Song]: Lista de canciones en la página
        """
        offset = (page - 1) * per_page
        query = """
        SELECT * FROM songs
        ORDER BY title COLLATE NOCASE
        LIMIT ? OFFSET ?
        """
        rows = self.db.execute_query(query, (per_page, offset))
        return [Song.from_db_row(row) for row in rows]
    
    def get_total_pages(self, per_page: int = 50) -> int:
        """
        Obtener número total de páginas
        
        Args:
            per_page: Canciones por página
            
        Returns:
            int: Número total de páginas
        """
        query = "SELECT COUNT(*) as total FROM songs"
        result = self.db.execute_query(query)[0]
        total = result["total"]
        return (total + per_page - 1) // per_page
    
    def search(self, title: str = "", artist: str = "", genre: str = "", 
              page: int = 1, per_page: int = 50) -> Tuple[List[Song], int]:
        """
        Buscar canciones con filtros
        
        Args:
            title: Filtro por título
            artist: Filtro por artista
            genre: Filtro por género
            page: Número de página
            per_page: Canciones por página
            
        Returns:
            Tuple[List[Song], int]: Lista de canciones que coinciden y el número total de canciones que coinciden con el filtro.
        """
        conditions = []
        where_params = []
        
        if title:
            conditions.append("LOWER(title) LIKE LOWER(?)")
            where_params.append(f"%{title}%")
        if artist:
            conditions.append("LOWER(artist) LIKE LOWER(?)")
            where_params.append(f"%{artist}%")
        if genre:
            conditions.append("LOWER(genre) LIKE LOWER(?)")
            where_params.append(f"%{genre}%")
            
        where_clause_str = "1=1"
        if conditions:
            where_clause_str = " AND ".join(conditions)
        
        count_query = f"SELECT COUNT(*) as total FROM songs WHERE {where_clause_str}"
        count_result = self.db.execute_query(count_query, tuple(where_params))
        total_items_matching_filter = count_result[0]['total'] if count_result and count_result[0] else 0
        
        offset = (page - 1) * per_page
        select_params = list(where_params)
        select_params.extend([per_page, offset])
        
        select_query = f"""
        SELECT * FROM songs
        WHERE {where_clause_str}
        ORDER BY title COLLATE NOCASE
        LIMIT ? OFFSET ?
        """
        
        rows = self.db.execute_query(select_query, tuple(select_params))
        songs = [Song.from_db_row(row) for row in rows]
        return songs, total_items_matching_filter
    
    def add(self, song: Song) -> int:
        """
        Agregar una nueva canción
        
        Args:
            song: Canción a agregar
            
        Returns:
            int: ID de la canción agregada
        """
        query = """
        INSERT INTO songs (title, artist, album, genre, bpm, file_path)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        params = (
            song.title,
            song.artist,
            song.album,
            song.genre,
            song.bpm,
            str(song.file_path)
        )
        self.db.execute_insert_update_delete(query, params)
        
        # Obtener el ID de la última inserción
        result = self.db.execute_query("SELECT last_insert_rowid() as id")[0]
        return result["id"]
    
    def exists(self, file_path: Path) -> bool:
        """
        Verificar si una canción ya existe por su ruta
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            bool: True si la canción existe
        """
        query = "SELECT COUNT(*) as count FROM songs WHERE file_path = ?"
        result = self.db.execute_query(query, (str(file_path),))[0]
        return result["count"] > 0

    def get_distinct_artists(self) -> List[str]:
        """Obtener lista de artistas distintos"""
        query = "SELECT DISTINCT artist FROM songs WHERE artist IS NOT NULL AND artist != '' ORDER BY artist COLLATE NOCASE"
        rows = self.db.execute_query(query)
        return [row['artist'] for row in rows]

    def get_distinct_genres(self) -> List[str]:
        """Obtener lista de géneros distintos"""
        query = "SELECT DISTINCT genre FROM songs WHERE genre IS NOT NULL AND genre != '' ORDER BY genre COLLATE NOCASE"
        rows = self.db.execute_query(query)
        return [row['genre'] for row in rows]

    def get_total_songs_count(self) -> int:
        """Obtener el número total de canciones en la base de datos."""
        query = "SELECT COUNT(*) as total FROM songs"
        result = self.db.execute_query(query)
        return result[0]['total'] if result and result[0] else 0
