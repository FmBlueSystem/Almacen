"""
Gestor de datos de la biblioteca
"""

from src.database.connection import DatabaseConnectionError, DatabaseTimeoutError
from src.utils.error_handler import LoadingCircuitBreaker, ErrorHandler

class LibraryDataManager:
    """Maneja la lógica de carga y gestión de datos de la biblioteca"""
    
    def __init__(self, music_service, logger):
        self.music_service = music_service
        self._logger = logger
        self._loading_circuit_breaker = LoadingCircuitBreaker(cooldown=2.0)

    def load_songs(self, page: int, filters: dict, per_page: int, on_data_loaded, on_status_message):
        """
        Cargar canciones aplicando filtros y paginación
        
        Args:
            page: Número de página a cargar
            filters: Diccionario con filtros {title, artist, genre}
            per_page: Cantidad de items por página
            on_data_loaded: Callback(songs, total_items) cuando los datos se cargan
            on_status_message: Callback(message) para mostrar mensajes de estado
        """
        if not self._loading_circuit_breaker.start_loading():
            self._logger.warning(f"Load request for page {page} blocked by circuit breaker")
            return

        try:
            songs, total_items = self._fetch_songs(
                page, 
                filters.get('title', ""),
                filters.get('artist', ""),
                filters.get('genre', ""),
                per_page
            )
            
            on_data_loaded(songs, total_items)
            on_status_message(
                f"Mostrando página {page}. {len(songs)} canciones (de {total_items} encontradas)."
            )
            
            self._loading_circuit_breaker.finish_loading(success=True)

        except (DatabaseConnectionError, DatabaseTimeoutError) as e:
            self._loading_circuit_breaker.finish_loading(success=False)
            error_msg = ErrorHandler.handle_db_error(self._logger, e, f"loading page {page}")
            on_status_message(error_msg)

        except Exception as e:
            self._loading_circuit_breaker.finish_loading(success=False)
            error_msg = ErrorHandler.handle_loading_error(self._logger, e, page)
            on_status_message(error_msg)

    def _fetch_songs(self, page: int, title: str, artist: str, genre: str, per_page: int):
        """Obtener canciones aplicando filtros"""
        if title or artist or genre:
            return self.music_service.search_songs(title, artist, genre, page, per_page)
        songs, _ = self.music_service.get_songs(page, per_page)
        total = self.music_service.get_total_songs_count()
        return songs, total

    def reset_loading_errors(self):
        """Resetear el estado de errores para permitir nuevos intentos de carga"""
        self._loading_circuit_breaker.reset_error_state()
        self._logger.info("Circuit breaker error state reset")
        return "Estado de errores reiniciado. Puede intentar cargar datos nuevamente."

    def update_library_metadata(self):
        """Obtener metadata actualizada de la biblioteca"""
        artists = self.music_service.get_distinct_artists()
        genres = self.music_service.get_distinct_genres()
        total_songs = self.music_service.get_total_songs_count()
        
        return {
            'total_songs': total_songs,
            'artists': artists,
            'genres': genres,
            'years': []
        }
