"""
Panel de reproducción con Material Design 3
"""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal

class PlaybackPanel(QFrame):
    """Panel de reproducción de música Material Design 3"""
    
    # Señales para solicitar acciones al AudioService
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal() # Nueva, si se añade botón de stop
    seek_requested = pyqtSignal(int)  # Posición en permil (0-1000) o milisegundos
    volume_change_requested = pyqtSignal(int)  # 0-100 (renombrado de volume_changed para claridad)
    next_requested = pyqtSignal()
    previous_requested = pyqtSignal()

    # Señales internas (si aún son útiles para otros propósitos, o pueden eliminarse si los slots las reemplazan)
    # play_state_changed = pyqtSignal(bool) 
    # volume_changed = pyqtSignal(int)  
    # progress_changed = pyqtSignal(int) 
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("playbackPanel")
        
        # Estado
        self.is_playing = False
        self.current_song = None
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 16)
        
        # Info de la canción
        self.create_song_info(layout)
        
        # Controles de reproducción
        self.create_playback_controls(layout)
        
        # Control de volumen
        self.create_volume_control(layout)
        
    def create_song_info(self, layout):
        """Crear sección de información de la canción"""
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        self.title_label = QLabel("Sin reproducción")
        self.title_label.setObjectName("playingTitle")
        info_layout.addWidget(self.title_label)
        
        # Artista
        self.artist_label = QLabel()
        self.artist_label.setObjectName("playingArtist")
        info_layout.addWidget(self.artist_label)
        
        layout.addWidget(info_frame)
        
    def create_playback_controls(self, layout):
        """Crear controles de reproducción"""
        controls = QFrame()
        controls.setObjectName("playbackControls")
        controls_layout = QHBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(16)
        
        # Botón anterior
        self.prev_button = QPushButton("⏮")
        self.prev_button.setObjectName("playbackButton")
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.previous_requested.emit)
        controls_layout.addWidget(self.prev_button)
        
        # Botón reproducir/pausar
        self.play_button = QPushButton("▶")
        self.play_button.setObjectName("playButton")
        self.play_button.clicked.connect(self.toggle_playback)
        controls_layout.addWidget(self.play_button)
        
        # Botón siguiente
        self.next_button = QPushButton("⏭")
        self.next_button.setObjectName("playbackButton")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.next_requested.emit)
        controls_layout.addWidget(self.next_button)
        
        # Barra de progreso
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        self.progress_slider.setRange(0, 1000) # Cambiado a 0-1000 para permil
        # Conectar sliderMoved para emitir seek_requested cuando el usuario arrastra
        self.progress_slider.sliderMoved.connect(self.on_progress_slider_moved)
        # valueChanged también podría usarse si queremos reaccionar a clics directos, 
        # pero sliderMoved es mejor para el arrastre del usuario.
        # self.progress_slider.valueChanged.connect(self.progress_changed.emit)
        controls_layout.addWidget(self.progress_slider)
        
        layout.addWidget(controls)
        
    def create_volume_control(self, layout):
        """Crear control de volumen"""
        volume = QFrame()
        volume.setObjectName("volumeControl")
        volume_layout = QHBoxLayout(volume)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        
        # Icono de volumen
        volume_icon = QLabel("🔊")
        volume_icon.setObjectName("volumeIcon")
        volume_layout.addWidget(volume_icon)
        
        # Slider de volumen
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75) # Valor inicial consistente con AudioControlBar
        self.volume_slider.valueChanged.connect(self.volume_change_requested.emit) # Conectar a nueva señal
        volume_layout.addWidget(self.volume_slider)
        
        layout.addWidget(volume)
        
    def set_current_song(self, song_info: dict):
        """
        Establecer canción actual
        
        Args:
            song_info: Diccionario con información de la canción {
                'title': str,
                'artist': str,
                'duration': int  # en segundos
            }
        """
        self.current_song = song_info
        self.title_label.setText(song_info['title'])
        self.artist_label.setText(song_info['artist'])
        self.progress_slider.setEnabled(True)
        self.play_button.setEnabled(True)
        
        # Actualizar botón de reproducción
        if self.is_playing:
            self.play_button.setText("⏸")
        else:
            self.play_button.setText("▶")
            
    def toggle_playback(self):
        """Alternar reproducción. Emite play_requested o pause_requested."""
        if not self.current_song:
            return
            
        if self.is_playing:
            self.pause_requested.emit()
        else:
            self.play_requested.emit()
        # El estado del botón se actualizará vía update_playback_state desde AudioService
        
    def update_progress(self, current_time_ms: int, total_time_ms: int):
        """Actualizar barra de progreso y etiquetas de tiempo (si las tuviera)."""
        if total_time_ms > 0:
            progress_permil = int((current_time_ms / total_time_ms) * 1000)
            # Solo actualizar si el usuario no está arrastrando el slider
            if not self.progress_slider.isSliderDown():
                 self.progress_slider.setValue(progress_permil)
        else:
            if not self.progress_slider.isSliderDown():
                self.progress_slider.setValue(0)
        
        # Si tuvieras QLabel para tiempos aquí, los actualizarías:
        # self.current_time_label.setText(self.format_time(current_time_ms))
        # self.total_time_label.setText(self.format_time(total_time_ms))

    def on_progress_slider_moved(self, position_permil: int):
        """Emitir señal seek_requested cuando el usuario mueve el slider de progreso."""
        self.seek_requested.emit(position_permil)

    def clear(self):
        """Limpiar panel"""
        self.current_song = None
        self.is_playing = False
        self.title_label.setText("Sin reproducción")
        self.artist_label.setText("")
        self.play_button.setText("▶")
        self.play_button.setEnabled(False)
        self.progress_slider.setValue(0)
        self.progress_slider.setEnabled(False)

    # --- Slots para ser llamados por AudioService ---
    def update_current_song(self, song_data: dict = None):
        """
        Establecer canción actual y su información en el panel.
        Llamado por AudioService cuando cambia la canción.
        """
        self.current_song = song_data
        if song_data:
            self.title_label.setText(song_data.get('title', "Desconocido"))
            self.artist_label.setText(song_data.get('artist', "Desconocido"))
            self.progress_slider.setEnabled(True)
            self.play_button.setEnabled(True)
            self.prev_button.setEnabled(True) # Habilitar si hay lógica de playlist
            self.next_button.setEnabled(True) # Habilitar si hay lógica de playlist
        else:
            self.title_label.setText("Sin reproducción")
            self.artist_label.setText("")
            self.progress_slider.setEnabled(False)
            self.progress_slider.setValue(0)
            self.play_button.setEnabled(False) # Deshabilitar si no hay canción
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
        
        # El estado de reproducción (play/pause) lo actualiza update_playback_state

    def update_playback_state(self, is_playing: bool, song_data_unused: dict = None):
        """
        Actualiza el estado de reproducción (play/pause) del botón.
        Llamado por AudioService.
        `song_data_unused` no se usa aquí ya que `update_current_song` maneja la info de la canción.
        """
        self.is_playing = is_playing
        if self.current_song: # Solo cambiar icono si hay una canción cargada
            self.play_button.setText("⏸" if self.is_playing else "▶")
            self.play_button.setEnabled(True)
        else: # No hay canción cargada
            self.play_button.setText("▶")
            self.play_button.setEnabled(False) # Botón de play deshabilitado si no hay canción
            self.is_playing = False # Asegurar que el estado interno es consistente
