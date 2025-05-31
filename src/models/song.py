"""
Modelo para la gestión de canciones
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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
        
    def create_table(self):
        """Crear tabla de canciones si no existe"""
        query = """
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            album TEXT NOT NULL,
            genre TEXT NOT NULL,
            bpm INTEGER,
            file_path TEXT UNIQUE NOT NULL
        )
        """
        self.db.execute_insert_update_delete(query)
        
        # Crear índices para búsqueda eficiente
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_songs_title ON songs(title)",
            "CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist)",
            "CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre)"
        ]
        for index in indexes:
            self.db.execute_insert_update_delete(index)
    
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
              page: int = 1, per_page: int = 50) -> list[Song]:
        """
        Buscar canciones con filtros
        
        Args:
            title: Filtro por título
            artist: Filtro por artista
            genre: Filtro por género
            page: Número de página
            per_page: Canciones por página
            
        Returns:
            list[Song]: Canciones que coinciden con los filtros
        """
        conditions = []
        params = []
        
        if title:
            conditions.append("title LIKE ?")
            params.append(f"%{title}%")
        if artist:
            conditions.append("artist LIKE ?")
            params.append(f"%{artist}%")
        if genre:
            conditions.append("genre LIKE ?")
            params.append(f"%{genre}%")
            
        where_clause = " AND ".join(conditions) if conditions else "1"
        offset = (page - 1) * per_page
        
        query = f"""
        SELECT * FROM songs
        WHERE {where_clause}
        ORDER BY title COLLATE NOCASE
        LIMIT ? OFFSET ?
        """
        params.extend([per_page, offset])
        
        rows = self.db.execute_query(query, tuple(params))
        return [Song.from_db_row(row) for row in rows]
    
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
