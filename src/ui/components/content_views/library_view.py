"""
Vista de biblioteca con Material Design 3
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QLineEdit, QPushButton, QApplication,
    QProgressBar
)
from PyQt6.QtCore import pyqtSignal, QSize, Qt, QTimer, QPropertyAnimation, QEasingCurve

from src.views.base_view import BaseView
from ..song_table import SongTable
from ...config import UIConfig

class LibraryView(QWidget, BaseView):
    """Vista principal de la biblioteca de música"""
    
    search_changed = pyqtSignal(str, str, str)
    view_changed = pyqtSignal(str)
    song_selection_changed = pyqtSignal(list, int)
    song_double_clicked = pyqtSignal(dict)
    page_changed_requested = pyqtSignal(int)
    
    def __init__(self, audio_service, parent=None):
        QWidget.__init__(self, parent)
        self.audio_service = audio_service
        self.current_page = 1
        self.total_pages = 1
        self.items_per_page = 50
        
        # Estado de carga y animaciones
        self.is_loading = False
        self._loading_animation = None
        
        # Debouncing para búsquedas
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._emit_search_changed)
        self._search_debounce_delay = 300
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)
        
        self.create_header(layout)
        self.create_filters(layout)
        
        # Indicador de carga
        self.loading_bar = QProgressBar()
        self.loading_bar.setObjectName("loadingBar")
        self.loading_bar.setTextVisible(False)
        self.loading_bar.setMaximumHeight(2)
        self.loading_bar.hide()
        layout.addWidget(self.loading_bar)
        
        self.create_table(layout)
        self.create_pagination_controls(layout)
        
        # Estado vacío
        self.empty_state = QLabel("No hay canciones que mostrar")
        self.empty_state.setObjectName("emptyState")
        self.empty_state.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_state.hide()
        layout.addWidget(self.empty_state)
        
        self.connect_audio_signals()
            
    def show_loading(self, show: bool = True):
        """Mostrar/ocultar indicador de carga con animación"""
        if show == self.is_loading:
            return
            
        self.is_loading = show
        if show:
            self.loading_bar.setValue(0)
            self.loading_bar.show()
            
            # Animar la barra de progreso
            if not self._loading_animation:
                self._loading_animation = QPropertyAnimation(self.loading_bar, b"value")
                self._loading_animation.setDuration(1000)
                self._loading_animation.setStartValue(0)
                self._loading_animation.setEndValue(100)
                self._loading_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
            
            self._loading_animation.start()
            
            # Deshabilitar controles durante la carga
            self.set_controls_enabled(False)
        else:
            if self._loading_animation:
                self._loading_animation.stop()
            self.loading_bar.hide()
            
            # Rehabilitar controles
            self.set_controls_enabled(True)

    def set_controls_enabled(self, enabled: bool):
        """Habilitar/deshabilitar controles de interacción"""
        self.search_field.setEnabled(enabled)
        self.artist_combo.setEnabled(enabled)
        self.genre_combo.setEnabled(enabled)
        self.view_selector.setEnabled(enabled)
        self.table.setEnabled(enabled)
        self.prev_button.setEnabled(enabled and self.current_page > 1)
        self.next_button.setEnabled(enabled and self.current_page < self.total_pages)

    def show_empty_state(self, show: bool = True):
        """Mostrar/ocultar estado vacío"""
        self.empty_state.setVisible(show)
        self.table.setVisible(not show)

    def load_songs(self, songs: list, total_items: int = None):
        """Cargar canciones en la tabla y actualizar paginación."""
        self.show_loading(True)
        
        # Simular una pequeña demora para la animación
        QTimer.singleShot(300, lambda: self._finish_loading_songs(songs, total_items))

    def _finish_loading_songs(self, songs: list, total_items: int = None):
        """Completar la carga de canciones después de la animación"""
        # Procesar canciones solo si no estamos en otro estado de carga
        if not self.is_loading:
            return
            
        self.table.load_songs(songs)
        
        if total_items is not None:
            if total_items == 0:
                self.total_pages = 1
                self.current_page = 1
            else:
                self.total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        else:
            self.total_pages = 1
            self.current_page = 1
            
        self.update_pagination_controls()
        self.show_loading(False)
        
        # Mostrar estado vacío si no hay canciones
        self.show_empty_state(len(songs) == 0)
        
    def update_ui_playback_state(self, is_playing: bool, song_data: dict = None):
        """Actualizar estado de reproducción en la interfaz"""
        current_song_from_service = self.audio_service.get_current_song_data()
        if is_playing and current_song_from_service:
            self.table.set_currently_playing_song(current_song_from_service)
        elif not is_playing and not current_song_from_service:
            self.table.clear_playing_indicator()
        elif not is_playing and current_song_from_service:
            self.table.set_currently_playing_song(current_song_from_service)
        else:
            self.table.clear_playing_indicator()

    def update_ui_current_song(self, song_data: dict = None):
        """Actualizar canción actual en la interfaz"""
        if song_data:
            self.table.set_currently_playing_song(song_data)
        else:
            self.table.clear_playing_indicator()

    def handle_playback_finished(self):
        """Manejar fin de reproducción"""
        print("[LibraryView] La canción ha terminado (señal de AudioService).")
        self.table.clear_playing_indicator()

    def create_header(self, layout):
        """Crear encabezado"""
        header = QFrame()
        header.setObjectName("contentHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title = QLabel("Biblioteca Musical")
        title.setObjectName("sectionTitle")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.view_selector = QComboBox()
        self.view_selector.setObjectName("viewSelector")
        self.view_selector.addItems(["Lista", "Cuadrícula"])
        self.view_selector.currentTextChanged.connect(self.view_changed.emit)
        header_layout.addWidget(self.view_selector)
        
        layout.addWidget(header)

    def create_filters(self, layout):
        """Crear filtros de búsqueda"""
        filter_frame = QFrame()
        filter_frame.setObjectName("filterSection")
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(16, 0, 16, 0)
        filter_layout.setSpacing(16)
        
        self.search_field = QLineEdit()
        self.search_field.setObjectName("searchField")
        self.search_field.setPlaceholderText("Buscar por título...")
        self.search_field.textChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.search_field)
        
        self.artist_combo = QComboBox()
        self.artist_combo.setObjectName("filterCombo")
        self.artist_combo.addItem("Todos los artistas")
        self.artist_combo.currentTextChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.artist_combo)
        
        self.genre_combo = QComboBox()
        self.genre_combo.setObjectName("filterCombo")
        self.genre_combo.addItem("Todos los géneros")
        self.genre_combo.currentTextChanged.connect(self.on_search_changed)
        filter_layout.addWidget(self.genre_combo)
        
        layout.addWidget(filter_frame)

    def create_table(self, layout):
        """Crear tabla de canciones"""
        self.table = SongTable()
        self.items_per_page = self.table.items_per_page
        layout.addWidget(self.table)
        
    def create_pagination_controls(self, main_layout: QVBoxLayout):
        """Crear controles de paginación"""
        pagination_container = QWidget()
        layout = QHBoxLayout(pagination_container)
        layout.setContentsMargins(0, 8, 0, 0)
        layout.setSpacing(16)

        self.prev_button = QPushButton("Anterior")
        self.prev_button.setObjectName("paginationButton")
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.go_to_previous_page)
        icon_prev = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ArrowBack)
        self.prev_button.setIcon(icon_prev)
        layout.addWidget(self.prev_button)

        self.page_label = QLabel(f"Página {self.current_page} de {self.total_pages}")
        self.page_label.setObjectName("paginationLabel")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.page_label)

        self.next_button = QPushButton("Siguiente")
        self.next_button.setObjectName("paginationButton")
        self.next_button.setEnabled(False)
        self.next_button.clicked.connect(self.go_to_next_page)
        icon_next = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ArrowForward)
        self.next_button.setIcon(icon_next)
        layout.addWidget(self.next_button)
        
        layout.addStretch()
        
        main_layout.addWidget(pagination_container)

    def update_pagination_controls(self):
        """Actualizar controles de paginación"""
        self.page_label.setText(f"Página {self.current_page} de {self.total_pages}")
        self.prev_button.setEnabled(self.current_page > 1 and not self.is_loading)
        self.next_button.setEnabled(self.current_page < self.total_pages and not self.is_loading)

    def go_to_previous_page(self):
        """Ir a la página anterior"""
        if self.current_page > 1 and not self.is_loading:
            self.current_page -= 1
            self.page_changed_requested.emit(self.current_page)

    def go_to_next_page(self):
        """Ir a la página siguiente"""
        if self.current_page < self.total_pages and not self.is_loading:
            self.current_page += 1
            self.page_changed_requested.emit(self.current_page)

    def update_filters(self, stats: dict):
        """Actualizar filtros con nuevos datos"""
        self.artist_combo.clear()
        self.artist_combo.addItem("Todos los artistas")
        self.artist_combo.addItems(sorted(stats.get('artists', [])))
        
        self.genre_combo.clear()
        self.genre_combo.addItem("Todos los géneros")
        self.genre_combo.addItems(sorted(stats.get('genres', [])))

    def on_search_changed(self):
        """Manejar cambios en los filtros de búsqueda"""
        self._search_timer.stop()
        self._search_timer.start(self._search_debounce_delay)
    
    def _emit_search_changed(self):
        """Emitir señal de búsqueda con filtros actuales"""
        if self.is_loading:
            return
            
        self.current_page = 1
        title = self.search_field.text()
        
        artist = self.artist_combo.currentText()
        if artist == "Todos los artistas":
            artist = ""
            
        genre = self.genre_combo.currentText()
        if genre == "Todos los géneros":
            genre = ""
            
        self.search_changed.emit(title, artist, genre)

    def clear(self):
        """Limpiar vista"""
        self.search_field.clear()
        self.artist_combo.setCurrentIndex(0)
        self.genre_combo.setCurrentIndex(0)
        self.table.clear()
        self.show_empty_state(True)

    def refresh(self):
        """Actualizar vista"""
        if hasattr(self.table, 'table') and self.table.table is not None:
            self.table.table.viewport().update()
        else:
            print("[LibraryView] Advertencia: self.table.table no disponible para refresh.")
            self.table.update()

    def connect_audio_signals(self):
        """Conectar señales relacionadas con la reproducción de audio"""
        if not self.audio_service:
            return
            
        # Conectar señales de la tabla con el servicio de audio
        self.table.song_double_clicked.connect(self.song_double_clicked.emit)
        self.table.song_selected.connect(self.song_selection_changed.emit)
        
        # Conectar señales del servicio de audio con la interfaz
        self.audio_service.playback_state_changed.connect(self.update_ui_playback_state)
        self.audio_service.current_song_changed.connect(self.update_ui_current_song)
        self.audio_service.playback_finished.connect(self.handle_playback_finished)
    
    def cleanup(self):
        """Limpiar recursos"""
        self.table.clear()
        self.clear()
        if self._loading_animation:
            self._loading_animation.stop()
