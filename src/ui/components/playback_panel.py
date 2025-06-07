"""
Panel de reproducción con Material Design 3
"""

from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTime
from PyQt6.QtGui import QPixmap, QKeySequence, QShortcut
import os

class PlaybackPanel(QFrame):
    """Panel de reproducción de música Material Design 3"""
    
    # Señales para solicitar acciones al AudioService
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)  # Posición en permil (0-1000)
    volume_change_requested = pyqtSignal(int)  # 0-100
    next_requested = pyqtSignal()
    previous_requested = pyqtSignal()
    repeat_mode_changed = pyqtSignal(int)  # 0: Off, 1: One, 2: All
    shuffle_mode_changed = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("playbackPanel")
        
        # Estado
        self.is_playing = False
        self.current_song = None
        self.repeat_mode = 0  # 0: Off, 1: One, 2: All
        self.shuffle_enabled = False
        self.current_time_ms = 0
        self.total_time_ms = 0
        
        # Estilo base del panel
        self.setStyleSheet("""
            QFrame#playbackPanel {
                background-color: #f3e8ff;
                border-top: 1px solid #d8b4fe;
                padding: 8px;
            }
            QLabel#playingTitle {
                color: #1e293b;
                font-size: 16px;
                font-weight: bold;
            }
            QLabel#playingArtist {
                color: #64748b;
                font-size: 14px;
            }
            QPushButton#playButton {
                background-color: #7c3aed;
                color: white;
                border: none;
                border-radius: 22px;
                font-size: 18px;
                padding: 8px;
                width: 44px;
                height: 44px;
            }
            QPushButton#playButton:hover {
                background-color: #6d28d9;
            }
            QPushButton#playButton:pressed {
                background-color: #5b21b6;
            }
            QPushButton#playbackButton {
                background-color: transparent;
                border: none;
                border-radius: 16px;
                font-size: 16px;
                padding: 4px;
                width: 32px;
                height: 32px;
            }
            QPushButton#playbackButton:hover {
                background-color: #ddd6fe;
            }
            QPushButton#playbackButton:pressed {
                background-color: #c4b5fd;
            }
            QPushButton#playbackButton:disabled {
                color: #94a3b8;
            }
            QSlider::groove:horizontal {
                border: none;
                background: #e2e8f0;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #7c3aed;
                border-radius: 2px;
            }
            QSlider::add-page:horizontal {
                background: #e2e8f0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #7c3aed;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #6d28d9;
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }
            QLabel#timeLabel {
                color: #64748b;
                font-size: 12px;
                min-width: 45px;
            }
            QLabel#volumeIcon {
                color: #64748b;
                font-size: 16px;
            }
        """)
        
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
        # Contenedor principal para carátula y texto
        song_info_main_frame = QFrame()
        song_info_main_layout = QHBoxLayout(song_info_main_frame)
        song_info_main_layout.setContentsMargins(0, 0, 0, 0)
        song_info_main_layout.setSpacing(12) # Espacio entre carátula e info

        # Etiqueta para la Carátula del Álbum
        self.album_art_label = QLabel()
        self.album_art_label.setObjectName("albumArtLabel")
        self.album_art_label.setFixedSize(QSize(64, 64))
        self.album_art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Estilo visual: borde, fondo y radio
        self.album_art_label.setStyleSheet("""
            QLabel#albumArtLabel {
                border: 2px solid #d8b4fe;
                border-radius: 8px;
                background: #f3e8ff;
            }
        """)
        # Placeholder visual (icono PNG)
        placeholder_path = os.path.join(os.path.dirname(__file__), '../../../assets/icons/album_placeholder.png')
        if os.path.exists(placeholder_path):
            self.album_art_placeholder = QPixmap(placeholder_path)
        else:
            self.album_art_placeholder = None
        if self.album_art_placeholder:
            self.album_art_label.setPixmap(self.album_art_placeholder.scaled(
                self.album_art_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        else:
            self.album_art_label.setText("🎵")
        self.album_art_label.setStyleSheet(self.album_art_label.styleSheet() + "font-size: 24px; color: #7c3aed;")
        song_info_main_layout.addWidget(self.album_art_label)

        # Contenedor para Título y Artista
        text_info_frame = QFrame()
        info_layout = QVBoxLayout(text_info_frame)
        info_layout.setContentsMargins(0, 0, 0, 0)
        
        # Título
        self.title_label = QLabel("Sin reproducción")
        self.title_label.setObjectName("playingTitle")
        info_layout.addWidget(self.title_label)
        
        # Artista
        self.artist_label = QLabel()
        self.artist_label.setObjectName("playingArtist")
        info_layout.addWidget(self.artist_label)
        
        song_info_main_layout.addWidget(text_info_frame)
        layout.addWidget(song_info_main_frame, 1) # Añadir el contenedor principal al layout principal con stretch
        
    def create_playback_controls(self, layout):
        """Crear controles de reproducción"""
        controls = QFrame()
        controls.setObjectName("playbackControls")
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        # Contenedor para botones
        buttons_container = QFrame()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.setSpacing(16)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Botones de reproducción
        self.shuffle_button = QPushButton("🔀")
        self.shuffle_button.setObjectName("playbackButton")
        self.shuffle_button.setToolTip("Aleatorio [S]")
        self.shuffle_button.clicked.connect(self.toggle_shuffle)
        buttons_layout.addWidget(self.shuffle_button)

        # Botón anterior
        self.prev_button = QPushButton("⏮")
        self.prev_button.setObjectName("playbackButton")
        self.prev_button.setEnabled(False)
        self.prev_button.setToolTip("Anterior [Ctrl+←]")
        self.prev_button.clicked.connect(self.previous_requested.emit)
        buttons_layout.addWidget(self.prev_button)
        
        # Botón reproducir/pausar
        self.play_button = QPushButton("▶")
        self.play_button.setObjectName("playButton")
        self.play_button.setToolTip("Reproducir/Pausar [Espacio]")
        self.play_button.clicked.connect(self.toggle_playback)
        buttons_layout.addWidget(self.play_button)
        
        # Botón siguiente
        self.next_button = QPushButton("⏭")
        self.next_button.setObjectName("playbackButton")
        self.next_button.setEnabled(False)
        self.next_button.setToolTip("Siguiente [Ctrl+→]")
        self.next_button.clicked.connect(self.next_requested.emit)
        buttons_layout.addWidget(self.next_button)

        # Botón repetir
        self.repeat_button = QPushButton("🔁")
        self.repeat_button.setObjectName("playbackButton")
        self.repeat_button.setToolTip("Repetir [R]")
        self.repeat_button.clicked.connect(self.toggle_repeat)
        buttons_layout.addWidget(self.repeat_button)

        controls_layout.addWidget(buttons_container)
        
        # Etiquetas de tiempo y barra de progreso
        progress_container = QFrame()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(8)

        self.time_current = QLabel("0:00")
        self.time_current.setObjectName("timeLabel")
        progress_layout.addWidget(self.time_current)

        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("progressSlider")
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setToolTip("Buscar")
        self.progress_slider.sliderMoved.connect(self.on_progress_slider_moved)
        progress_layout.addWidget(self.progress_slider)

        self.time_total = QLabel("0:00")
        self.time_total.setObjectName("timeLabel")
        progress_layout.addWidget(self.time_total)

        controls_layout.addWidget(progress_container)
        
        layout.addWidget(controls, 2)
        
    def create_volume_control(self, layout):
        """Crear control de volumen"""
        volume = QFrame()
        volume.setObjectName("volumeControl")
        volume_layout = QHBoxLayout(volume)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(8)
        volume_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        # Control de volumen con icono dinámico
        self.volume_icon = QLabel("🔊")
        self.volume_icon.setObjectName("volumeIcon")
        self.volume_icon.setToolTip("Silenciar [M]")
        self.volume_icon.mousePressEvent = lambda _: self.toggle_mute()
        volume_layout.addWidget(self.volume_icon)
        
        # Slider de volumen
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("volumeSlider")
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setFixedWidth(100)
        self.volume_slider.setToolTip("Ajustar volumen [↑/↓]")
        self.volume_slider.valueChanged.connect(self.on_volume_changed)
        volume_layout.addWidget(self.volume_slider)

        # Atajos de teclado
        self.setup_shortcuts()
        
        layout.addWidget(volume, 1)
        
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
        
    def setup_shortcuts(self):
        """Configurar atajos de teclado"""
        QShortcut(QKeySequence(Qt.Key.Key_Space), self, self.toggle_playback)
        QShortcut(QKeySequence(Qt.Key.Key_M), self, self.toggle_mute)
        QShortcut(QKeySequence(Qt.Key.Key_R), self, self.toggle_repeat)
        QShortcut(QKeySequence(Qt.Key.Key_S), self, self.toggle_shuffle)
        
        QShortcut(QKeySequence(Qt.Key.Key_Left), self, lambda: self.seek_relative(-5000))
        QShortcut(QKeySequence(Qt.Key.Key_Right), self, lambda: self.seek_relative(5000))
        QShortcut(QKeySequence("Ctrl+Left"), self, self.previous_requested.emit)
        QShortcut(QKeySequence("Ctrl+Right"), self, self.next_requested.emit)
        
        QShortcut(QKeySequence(Qt.Key.Key_Up), self, lambda: self.adjust_volume(5))
        QShortcut(QKeySequence(Qt.Key.Key_Down), self, lambda: self.adjust_volume(-5))

    def update_progress(self, current_time_ms: int, total_time_ms: int):
        """Actualizar barra de progreso y etiquetas de tiempo."""
        self.current_time_ms = current_time_ms
        self.total_time_ms = total_time_ms
        
        if total_time_ms > 0:
            progress_permil = int((current_time_ms / total_time_ms) * 1000)
            if not self.progress_slider.isSliderDown():
                self.progress_slider.setValue(progress_permil)
        else:
            if not self.progress_slider.isSliderDown():
                self.progress_slider.setValue(0)
        
        # Actualizar etiquetas de tiempo
        self.time_current.setText(self.format_time(current_time_ms))
        self.time_total.setText(self.format_time(total_time_ms))

    def format_time(self, ms: int) -> str:
        """Formatear tiempo en milisegundos a MM:SS"""
        total_seconds = int(ms / 1000)
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"

    def seek_relative(self, offset_ms: int):
        """Buscar relativamente a la posición actual"""
        if not self.current_song:
            return
        new_position = max(0, min(self.current_time_ms + offset_ms, self.total_time_ms))
        if self.total_time_ms > 0:
            self.seek_requested.emit(int((new_position / self.total_time_ms) * 1000))

    def toggle_repeat(self):
        """Alternar modo de repetición"""
        self.repeat_mode = (self.repeat_mode + 1) % 3
        icons = ["↩️", "🔂", "🔁"]
        tooltips = ["Repetir [R]: Off", "Repetir [R]: Una", "Repetir [R]: Todas"]
        self.repeat_button.setText(icons[self.repeat_mode])
        self.repeat_button.setToolTip(tooltips[self.repeat_mode])
        self.repeat_mode_changed.emit(self.repeat_mode)

    def toggle_shuffle(self):
        """Alternar modo aleatorio"""
        self.shuffle_enabled = not self.shuffle_enabled
        self.shuffle_button.setText("🔀")
        self.shuffle_button.setStyleSheet(
            f"background-color: {'#7c3aed' if self.shuffle_enabled else 'transparent'}; color: {'white' if self.shuffle_enabled else '#1e293b'};"
        )
        self.shuffle_button.setToolTip(f"Aleatorio [S]: {'On' if self.shuffle_enabled else 'Off'}")
        self.shuffle_mode_changed.emit(self.shuffle_enabled)

    def toggle_mute(self):
        """Alternar silencio"""
        if self.volume_slider.value() > 0:
            self.previous_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
        else:
            self.volume_slider.setValue(self.previous_volume if hasattr(self, 'previous_volume') else 75)

    def adjust_volume(self, delta: int):
        """Ajustar volumen en incrementos"""
        self.volume_slider.setValue(self.volume_slider.value() + delta)

    def on_volume_changed(self, value: int):
        """Actualizar icono de volumen y emitir señal"""
        if value == 0:
            self.volume_icon.setText("🔇")
        elif value < 33:
            self.volume_icon.setText("🔈")
        elif value < 66:
            self.volume_icon.setText("🔉")
        else:
            self.volume_icon.setText("🔊")
        self.volume_change_requested.emit(value)

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
        self.album_art_label.clear()

    # --- Slots para ser llamados por AudioService ---
    def update_current_song(self, song_data: dict = None):
        """
        Establecer canción actual y su información en el panel.
        Llamado por AudioService cuando cambia la canción.
        """
        self.current_song = song_data
        if song_data:
            print(f"[PlaybackPanel] update_current_song RECIBIDO: {song_data}") # DEBUG
            self.title_label.setText(song_data.get('title', "Desconocido"))
            self.artist_label.setText(song_data.get('artist', "Desconocido"))
            self.progress_slider.setEnabled(True)
            self.play_button.setEnabled(True)
            self.prev_button.setEnabled(True) # Habilitar si hay lógica de playlist
            self.next_button.setEnabled(True) # Habilitar si hay lógica de playlist

            # Actualizar carátula
            album_art_pixmap = song_data.get('album_art')
            if album_art_pixmap and isinstance(album_art_pixmap, QPixmap) and not album_art_pixmap.isNull():
                print(f"[PlaybackPanel] Mostrando carátula: {album_art_pixmap}") # DEBUG
                self.album_art_label.setPixmap(album_art_pixmap.scaled(
                    self.album_art_label.size(), 
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                self.album_art_label.setText("") # Quitar placeholder
            else:
                print(f"[PlaybackPanel] No hay carátula (o es inválida) en song_data. Pixmap: {album_art_pixmap}") # DEBUG
                if self.album_art_placeholder:
                    self.album_art_label.setPixmap(self.album_art_placeholder.scaled(
                        self.album_art_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    ))
                    self.album_art_label.setText("")
                else:
                    self.album_art_label.clear()
                    self.album_art_label.setText("🎵") # Fallback emoji

        else:
            print("[PlaybackPanel] update_current_song RECIBIDO None") # DEBUG
            self.title_label.setText("Sin reproducción")
            self.artist_label.setText("")
            self.progress_slider.setEnabled(False)
            self.progress_slider.setValue(0)
            self.play_button.setEnabled(False) # Deshabilitar si no hay canción
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            if self.album_art_placeholder:
                self.album_art_label.setPixmap(self.album_art_placeholder.scaled(
                    self.album_art_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
                self.album_art_label.setText("")
            else:
                self.album_art_label.clear()
                self.album_art_label.setText("🎵") # Placeholder visual
        
        # El estado de reproducción (play/pause) lo actualiza update_playback_state

    def update_playback_state(self, is_playing: bool, song_data_unused: dict = None):
        """
        Actualiza el estado de reproducción (play/pause) del botón.
        Llamado por AudioService.
        `song_data_unused` no se usa aquí ya que `update_current_song` maneja la info de la canción.
        """
        print(f"[PlaybackPanel] update_playback_state RECIBIDO: is_playing={is_playing}, song_data={song_data_unused}") # DEBUG
        self.is_playing = is_playing
        if self.current_song: # Solo cambiar icono si hay una canción cargada
            self.play_button.setText("⏸" if self.is_playing else "▶")
            self.play_button.setEnabled(True)
        else: # No hay canción cargada
            self.play_button.setText("▶")
            self.play_button.setEnabled(False) # Botón de play deshabilitado si no hay canción
            self.is_playing = False # Asegurar que el estado interno es consistente
