"""
Servicio para gestionar la reproducción de archivos de audio.
Utiliza QMediaPlayer de PyQt6.QtMultimedia.
"""

from PyQt6.QtCore import QObject, pyqtSignal, QUrl, QStandardPaths
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

class AudioService(QObject):
    """
    Servicio de reproducción de audio.
    Gestiona la carga, reproducción, pausa, parada, búsqueda y volumen de pistas de audio.
    Emite señales para actualizar la interfaz de usuario sobre el estado de la reproducción.
    """

    # Señales para la UI
    # bool: is_playing, dict|None: current_song_data (None si no hay canción)
    playback_state_changed = pyqtSignal(bool, object)
    # int: current_time_ms, int: total_time_ms
    song_progress_updated = pyqtSignal(int, int)
    # dict|None: new_song_data (None si se detiene y no hay siguiente)
    current_song_changed = pyqtSignal(object)
    # str: error_message
    error_occurred = pyqtSignal(str)
    
    # Señal para cuando una canción termina y no hay una siguiente (o no es modo continuo)
    playback_finished = pyqtSignal()
    
    # Señales para navegación de canciones
    previous_available = pyqtSignal(bool)
    next_available = pyqtSignal(bool)


    def __init__(self, parent=None):
        super().__init__(parent)
        
        self._player = QMediaPlayer(self)
        self._audio_output = QAudioOutput(self) # Necesario desde Qt6 para que suene
        self._player.setAudioOutput(self._audio_output)
        
        print("[AudioService] Inicializando...")
        self._current_song_data = None
        self._playlist = []  # Lista de reproducción actual
        self._current_index = -1  # Índice de la canción actual en la lista
        self._is_intentionally_stopped = True # Para distinguir stop de fin de canción
        
        # Configuración inicial
        self._audio_output.setVolume(0.5)  # Volumen inicial al 50%
        print("[AudioService] Inicializado correctamente.")

        # Conectar señales internas del QMediaPlayer
        self._player.mediaStatusChanged.connect(self._handle_media_status_changed)
        self._player.positionChanged.connect(self._handle_position_changed)
        self._player.durationChanged.connect(self._handle_duration_changed)
        self._player.errorOccurred.connect(self._handle_player_error)
        self._player.playingChanged.connect(self._handle_playing_changed)


    # --- Métodos de Control ---

    def play_song(self, song_data: dict):
        """
        Carga y reproduce una nueva canción.

        Args:
            song_data (dict): Diccionario con información de la canción,
                              debe incluir 'file_path'.
        """
        if not song_data or 'file_path' not in song_data:
            self.error_occurred.emit("Datos de canción inválidos o ruta de archivo faltante.")
            return

        file_path = song_data.get('file_path')
        url = QUrl.fromLocalFile(file_path)
        
        if not url.isValid():
            self.error_occurred.emit(f"Ruta de archivo inválida: {file_path}")
            self._current_song_data = None
            self.current_song_changed.emit(None)
            self.playback_state_changed.emit(False, None)
            return

        self._is_intentionally_stopped = False
        self._current_song_data = song_data
        
        if self._player.source() == url: # Misma canción, podría ser un play después de pausa
            if self._player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
                self._player.play()
            elif self._player.playbackState() == QMediaPlayer.PlaybackState.StoppedState:
                 # Si estaba detenida (ej. error previo o fin), volver a cargar y reproducir.
                 self._player.setSource(url)
                 self._player.play()
        else: # Nueva canción
            self._player.setSource(url)
            self._player.play()
        
        # Emitir cambio de canción inmediatamente, estado de reproducción lo emitirá _handle_playing_changed
        self.current_song_changed.emit(self._current_song_data)
        # self.playback_state_changed.emit(True, self._current_song_data) # Se maneja con playingChanged

    def pause(self):
        """Pausa la reproducción actual."""
        if self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self._player.pause()
            # self.playback_state_changed.emit(False, self._current_song_data) # Se maneja con playingChanged

    def resume(self):
        """Reanuda la reproducción si está pausada."""
        if self._current_song_data and self._player.playbackState() == QMediaPlayer.PlaybackState.PausedState:
            self._player.play()
            # self.playback_state_changed.emit(True, self._current_song_data) # Se maneja con playingChanged

    def stop(self):
        """Detiene la reproducción actual."""
        self._is_intentionally_stopped = True
        self._player.stop()
        # self.playback_state_changed.emit(False, None) # Se maneja con playingChanged y mediaStatusChanged
        # self.current_song_changed.emit(None)          # Se maneja con playingChanged y mediaStatusChanged
        # self._current_song_data = None # Se limpia en _handle_media_status_changed si es Stop


    def seek(self, position_permil: int):
        """
        Busca una posición específica en la canción actual.

        Args:
            position_permil (int): Posición deseada como permil (0-1000) de la duración total.
        """
        if self._player.duration() > 0:
            target_ms = int((position_permil / 1000.0) * self._player.duration())
            self._player.setPosition(target_ms)

    def set_volume(self, volume_percentage: int):
        """
        Establece el volumen de reproducción.

        Args:
            volume_percentage (int): Volumen deseado (0-100).
        """
        # QAudioOutput usa una escala de 0.0 a 1.0
        volume_float = max(0.0, min(1.0, volume_percentage / 100.0))
        self._audio_output.setVolume(volume_float)

    # --- Métodos de Información ---

    def get_current_song_data(self) -> dict | None:
        """Devuelve los datos de la canción actual o None."""
        return self._current_song_data

    def is_playing(self) -> bool:
        """Devuelve True si el reproductor está actualmente en estado de reproducción."""
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        
    def get_total_duration_ms(self) -> int:
        """Devuelve la duración total de la canción actual en milisegundos."""
        return self._player.duration()

    def play_previous(self):
        """Reproducir la canción anterior en la lista."""
        if self.has_previous():
            self._current_index -= 1
            self.play_song(self._playlist[self._current_index])
            self._update_navigation_status()
    
    def play_next(self):
        """Reproducir la siguiente canción en la lista."""
        if self.has_next():
            self._current_index += 1
            self.play_song(self._playlist[self._current_index])
            self._update_navigation_status()
            
    def set_playlist(self, songs: list[dict], start_index: int = 0):
        """
        Establecer la lista de reproducción actual.
        
        Args:
            songs: Lista de diccionarios con información de canciones
            start_index: Índice de la canción por la que empezar
        """
        self._playlist = songs
        self._current_index = max(0, min(start_index, len(songs) - 1)) if songs else -1
        self._update_navigation_status()
        
    def has_previous(self) -> bool:
        """Verificar si hay una canción anterior disponible."""
        return self._current_index > 0

    def has_next(self) -> bool:
        """Verificar si hay una siguiente canción disponible."""
        return 0 <= self._current_index < len(self._playlist) - 1
        
    def _update_navigation_status(self):
        """Actualizar y emitir el estado de navegación."""
        self.previous_available.emit(self.has_previous())
        self.next_available.emit(self.has_next())

    # --- Slots Privados para Señales de QMediaPlayer ---

    def _handle_media_status_changed(self, status: QMediaPlayer.MediaStatus):
        """Maneja los cambios en el estado del medio."""
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            print("[AudioService] Media cargada.")
            # self.playback_state_changed.emit(self.is_playing(), self._current_song_data)
            # self.song_progress_updated.emit(0, self._player.duration())
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("[AudioService] Fin de la canción.")
            if not self._is_intentionally_stopped:
                if self.has_next():
                    self.play_next()  # Reproducir siguiente canción si está disponible
                else:
                    self.stop()  # Si no hay siguiente, detener reproducción
                    self.playback_finished.emit()
            # Si fue un stop intencional, _handle_playing_changed ya lo manejó.
            # No emitir playback_state_changed aquí para evitar redundancia si _player.stop() ya lo hizo
            
        elif status == QMediaPlayer.MediaStatus.InvalidMedia:
            print("[AudioService] Media inválida.")
            self.error_occurred.emit(f"No se pudo cargar el archivo: {self._current_song_data.get('file_path') if self._current_song_data else 'desconocido'}. Formato no soportado o archivo corrupto.")
            self._current_song_data = None
            self.current_song_changed.emit(None)
            self.playback_state_changed.emit(False, None)
            self.song_progress_updated.emit(0,0)

        elif status == QMediaPlayer.MediaStatus.NoMedia:
            print("[AudioService] NoMedia - usualmente después de stop().")
            # Si es un stop intencional, _handle_playing_changed(False) ya debería haberse emitido.
            # Si _current_song_data no es None aquí, es un estado inconsistente.
            if self._is_intentionally_stopped: # Asegurar limpieza final en caso de stop.
                 self._current_song_data = None
                 self.current_song_changed.emit(None)
                 self.playback_state_changed.emit(False, None)
                 self.song_progress_updated.emit(0,0)


    def _handle_position_changed(self, position_ms: int):
        """Maneja los cambios en la posición de reproducción."""
        self.song_progress_updated.emit(position_ms, self._player.duration())

    def _handle_duration_changed(self, duration_ms: int):
        """Maneja los cambios en la duración del medio (cuando se carga)."""
        # Actualizar el progreso una vez que la duración es conocida
        self.song_progress_updated.emit(self._player.position(), duration_ms)

    def _handle_player_error(self, error: QMediaPlayer.Error, error_string: str):
        """Maneja errores del QMediaPlayer."""
        print(f"[AudioService] Error del reproductor: {error} - {error_string}")
        self.error_occurred.emit(f"Error de reproducción: {error_string}")
        self._current_song_data = None
        self.current_song_changed.emit(None)
        self.playback_state_changed.emit(False, None) # Error implica no reproducción
        self.song_progress_updated.emit(0,0)

    def _handle_playing_changed(self, playing: bool):
        """
        Maneja el cambio de estado de reproducción del QMediaPlayer (señal playingChanged).
        Esta señal es más directa para el estado play/pause que mediaStatusChanged o playbackStateChanged.
        """
        print(f"[AudioService] playingChanged: {playing}")
        if playing:
            self.playback_state_changed.emit(True, self._current_song_data)
        else:
            # Si 'playing' es False, puede ser pausa, stop, o fin de canción.
            # _is_intentionally_stopped ayuda a distinguir.
            # Si es stop intencional o fin de canción (que llama a stop), _current_song_data se limpia.
            # Durante cleanup() o cuando no hay canción activa, enviamos None
            if (self._player.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia and self._is_intentionally_stopped) or \
               (self._is_intentionally_stopped or self._player.mediaStatus() == QMediaPlayer.MediaStatus.EndOfMedia):
                current_data_for_signal = None
            else:
                # En otros casos, preservamos _current_song_data o enviamos None
                current_data_for_signal = self._current_song_data if isinstance(self._current_song_data, dict) else None
            
            self.playback_state_changed.emit(False, current_data_for_signal)
            
            if self._player.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia and self._is_intentionally_stopped : # Estado final de un stop
                 self._current_song_data = None # Asegurar que esté limpio
                 self.current_song_changed.emit(None)
                 self.song_progress_updated.emit(0,0)
                 # Resetear lista de reproducción al detener
                 self._playlist = []
                 self._current_index = -1
                 self._update_navigation_status()

    def cleanup(self):
        """Limpiar recursos antes de destruir el objeto."""
        print("[AudioService] Limpiando servicio de audio...")
        self.stop()
        self._player.setSource(QUrl()) # Liberar la fuente actual
        # self._player.deleteLater() # QMediaPlayer es hijo de self (QObject), se destruirá con él
        # self._audio_output.deleteLater()
