"""
Widget para los controles de reproducción de audio.
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLabel, QSlider
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QIcon

# Suponiendo que tienes iconos en assets/icons
# Ejemplo de rutas (ajusta según tu estructura)
PLAY_ICON_PATH = "assets/icons/play.svg"
PAUSE_ICON_PATH = "assets/icons/pause.svg"
STOP_ICON_PATH = "assets/icons/stop.svg"
PREVIOUS_ICON_PATH = "assets/icons/previous.svg"
NEXT_ICON_PATH = "assets/icons/next.svg"
VOLUME_ICON_PATH = "assets/icons/volume.svg"

class AudioControlBar(QWidget):
    """
    Barra de controles para la reproducción de audio.
    Incluye botones de play/pausa, stop, anterior/siguiente,
    una barra de progreso y un control de volumen.
    """
    
    # Señales para comunicar acciones del usuario
    play_requested = pyqtSignal()
    pause_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    seek_requested = pyqtSignal(int)  # Posición en milisegundos o porcentaje
    volume_changed = pyqtSignal(int) # Porcentaje de volumen
    next_requested = pyqtSignal()
    previous_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_playing = False
        self.init_ui()

    def init_ui(self):
        """Inicializar la interfaz de usuario de la barra de controles."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5) # Márgenes ajustados
        layout.setSpacing(10)

        # Botón de Anterior
        self.previous_button = QPushButton(QIcon(PREVIOUS_ICON_PATH), "")
        self.previous_button.setObjectName("audioControlButton")
        self.previous_button.setToolTip("Anterior")
        self.previous_button.clicked.connect(self.previous_requested.emit)
        layout.addWidget(self.previous_button)

        # Botón de Play/Pausa
        self.play_pause_button = QPushButton(QIcon(PLAY_ICON_PATH), "")
        self.play_pause_button.setObjectName("audioPlayPauseButton")
        self.play_pause_button.setToolTip("Reproducir")
        self.play_pause_button.clicked.connect(self.toggle_play_pause)
        layout.addWidget(self.play_pause_button)

        # Botón de Stop
        self.stop_button = QPushButton(QIcon(STOP_ICON_PATH), "")
        self.stop_button.setObjectName("audioControlButton")
        self.stop_button.setToolTip("Detener")
        self.stop_button.clicked.connect(self.stop_requested.emit)
        layout.addWidget(self.stop_button)
        
        # Botón de Siguiente
        self.next_button = QPushButton(QIcon(NEXT_ICON_PATH), "")
        self.next_button.setObjectName("audioControlButton")
        self.next_button.setToolTip("Siguiente")
        self.next_button.clicked.connect(self.next_requested.emit)
        layout.addWidget(self.next_button)

        # Etiqueta de tiempo transcurrido
        self.current_time_label = QLabel("00:00")
        self.current_time_label.setObjectName("audioTimeLabel")
        layout.addWidget(self.current_time_label)

        # Barra de progreso (seek bar)
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setObjectName("audioProgressSlider")
        self.progress_slider.setRange(0, 1000) # Representa progreso (ej. 0-1000 para permil)
        self.progress_slider.sliderMoved.connect(self.on_seek) # Cuando el usuario arrastra
        self.progress_slider.valueChanged.connect(self.on_seek_by_click) # Cuando hace clic
        layout.addWidget(self.progress_slider, 1) # El 1 da más espacio al slider

        # Etiqueta de tiempo total
        self.total_time_label = QLabel("00:00")
        self.total_time_label.setObjectName("audioTimeLabel")
        layout.addWidget(self.total_time_label)

        # Icono de Volumen (opcional, podría ser un botón que abre un QMenu o un QSlider directamente)
        self.volume_icon = QLabel()
        self.volume_icon.setPixmap(QIcon(VOLUME_ICON_PATH).pixmap(16, 16)) # Ajustar tamaño
        layout.addWidget(self.volume_icon)

        # Control de Volumen
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setObjectName("audioVolumeSlider")
        self.volume_slider.setRange(0, 100) # 0-100%
        self.volume_slider.setValue(75) # Volumen inicial
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.volume_slider.setFixedWidth(100) # Ancho fijo para el slider de volumen
        layout.addWidget(self.volume_slider)
        
        self.setLayout(layout)

    def toggle_play_pause(self):
        """Alternar entre reproducir y pausar."""
        if self._is_playing:
            self.pause_requested.emit()
        else:
            self.play_requested.emit()

    def set_playing_state(self, playing: bool):
        """Actualizar el estado de reproducción y el icono del botón."""
        self._is_playing = playing
        if playing:
            self.play_pause_button.setIcon(QIcon(PAUSE_ICON_PATH))
            self.play_pause_button.setToolTip("Pausar")
        else:
            self.play_pause_button.setIcon(QIcon(PLAY_ICON_PATH))
            self.play_pause_button.setToolTip("Reproducir")

    def update_progress(self, current_time_ms: int, total_time_ms: int):
        """
        Actualizar la barra de progreso y las etiquetas de tiempo.
        
        Args:
            current_time_ms: Tiempo transcurrido en milisegundos.
            total_time_ms: Duración total en milisegundos.
        """
        if total_time_ms > 0:
            self.progress_slider.setValue(int((current_time_ms / total_time_ms) * 1000))
        else:
            self.progress_slider.setValue(0)
            
        self.current_time_label.setText(self.format_time(current_time_ms))
        self.total_time_label.setText(self.format_time(total_time_ms))

    def on_seek(self, position_permil: int):
        """Manejar el arrastre del slider de progreso."""
        # Solo emitir si el usuario es quien mueve el slider (no actualizaciones programáticas)
        if self.progress_slider.isSliderDown():
            self.seek_requested.emit(position_permil)
            
    def on_seek_by_click(self, position_permil: int):
        """Manejar el clic en el slider de progreso que no sea un arrastre."""
        # Evitar doble emisión si también se disparó sliderMoved
        if not self.progress_slider.isSliderDown():
             self.seek_requested.emit(position_permil)

    @staticmethod
    def format_time(ms: int) -> str:
        """Formatear tiempo de milisegundos a MM:SS."""
        if ms < 0: ms = 0
        seconds = (ms // 1000) % 60
        minutes = (ms // (1000 * 60)) % 60
        # hours = (ms // (1000 * 60 * 60)) % 24 # Descomentar si se necesitan horas
        return f"{minutes:02d}:{seconds:02d}"

    def set_enabled_controls(self, enabled: bool):
        """Habilitar o deshabilitar todos los controles."""
        self.previous_button.setEnabled(enabled)
        self.play_pause_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)
        self.progress_slider.setEnabled(enabled)
        self.volume_slider.setEnabled(enabled) # El volumen podría quererse habilitado siempre

    # Aquí se podrían añadir métodos para manejar el cambio de tema, escala, etc.
    # def on_theme_changed(self, is_dark: bool): ...
    # def on_scale_changed(self, scale_factor: float): ... 
