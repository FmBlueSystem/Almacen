"""
Vista de biblioteca con Material Design 3
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QComboBox, QLineEdit, QPushButton, QApplication
)
from PyQt6.QtCore import pyqtSignal, QSize, Qt, QTimer

from src.views.base_view import BaseView
from ..song_table import SongTable
from ...config import UIConfig

class LibraryView(QWidget, BaseView):
    """Vista principal de la biblioteca de música"""
    
    search_changed = pyqtSignal(str, str, str)
    view_changed = pyqtSignal(str)
    song_selection_changed = pyqtSignal(list, int)  # Lista de canciones y índice seleccionado
    song_double_clicked = pyqtSignal(dict)  # Reenvía la señal de la tabla
    page_changed_requested = pyqtSignal(int) # Nueva señal para solicitar cambio de página
    
    def __init__(self, audio_service, parent=None):
        QWidget.__init__(self, parent)
        self.audio_service = audio_service
        self.current_page = 1
        self.total_pages = 1
        self.items_per_page = 50 # Podría venir de config o SongTable
        
        # Debouncing para búsquedas
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._emit_search_changed)
        self._search_debounce_delay = 300  # 300ms de delay
        
        self.init_ui()
        
    def init_ui(self):
        """Inicializar interfaz"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16) # Reducido un poco para más espacio para paginación
        
        self.create_header(layout)
        self.create_filters(layout)
        self.create_table(layout)
        self.create_pagination_controls(layout) # Añadir controles de paginación
        
        self.connect_audio_signals() 
        
        if self.audio_service:
            self.audio_service.playback_state_changed.connect(self.update_ui_playback_state)
            self.audio_service.current_song_changed.connect(self.update_ui_current_song)
            self.audio_service.playback_finished.connect(self.handle_playback_finished)

    def connect_audio_signals(self):
        """Conectar señales de los componentes de audio a los manejadores."""
        # Conectar señales de la tabla
        self.table.song_double_clicked.connect(self.handle_song_double_clicked)
        self.table.song_selected.connect(self.on_song_selected)

    def handle_song_double_clicked(self, song_data: dict):
        """Propagar señal de doble clic."""
        self.song_double_clicked.emit(song_data)

    def on_song_selected(self, song_data: dict):
        """Manejar selección de canción en la tabla."""
        if song_data:
            # Obtener todas las canciones de la tabla y el índice de la seleccionada
            songs = []
            selected_index = -1
            
            for row in range(self.table.table.rowCount()):
                item_data = self.table.table.item(row, 1).data(Qt.ItemDataRole.UserRole)
                if item_data:
                    songs.append(item_data)
                    if item_data.get('file_path') == song_data.get('file_path'):
                        selected_index = len(songs) - 1
                        
            if songs and selected_index >= 0:
                self.song_selection_changed.emit(songs, selected_index)
    
    def update_ui_playback_state(self, is_playing: bool, song_data: dict = None):
        """Actualiza el indicador en la tabla basado en el estado de reproducción."""
        current_song_from_service = self.audio_service.get_current_song_data()
        if is_playing and current_song_from_service:
            self.table.set_currently_playing_song(current_song_from_service)
        elif not is_playing and not current_song_from_service: # Stop completo
            self.table.clear_playing_indicator()
        elif not is_playing and current_song_from_service: # Pausado
            self.table.set_currently_playing_song(current_song_from_service) # Mantener indicador si está pausado
        else: # Otros casos, limpiar por si acaso
             self.table.clear_playing_indicator()

    def update_ui_current_song(self, song_data: dict = None):
        """Actualiza qué canción se muestra como activa en la tabla."""
        if song_data:
            self.table.set_currently_playing_song(song_data)
        else: 
            self.table.clear_playing_indicator()

    def handle_playback_finished(self):
        print("[LibraryView] La canción ha terminado (señal de AudioService).")
        self.table.clear_playing_indicator()

    def get_minimum_size(self) -> QSize:
        """Obtener tamaño mínimo"""
        base_width, base_height = UIConfig.get_base_resolution()
        return QSize(base_width // 2, base_height // 2)
    
    def get_preferred_size(self) -> QSize:
        """Obtener tamaño preferido"""
        return QSize(*UIConfig.get_base_resolution())
        
    def create_header(self, layout):
        """Crear header de la vista"""
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
        """Crear barra de filtros"""
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
        self.items_per_page = self.table.items_per_page # Sincronizar items_per_page
        layout.addWidget(self.table)
        
    def create_pagination_controls(self, main_layout: QVBoxLayout):
        """Crear controles de paginación (Anterior, Siguiente, Indicador de página)"""
        pagination_container = QWidget()
        layout = QHBoxLayout(pagination_container)
        layout.setContentsMargins(0, 8, 0, 0) # Margen superior
        layout.setSpacing(16)

        self.prev_button = QPushButton("Anterior")
        self.prev_button.setObjectName("paginationButton")
        self.prev_button.setEnabled(False)
        self.prev_button.clicked.connect(self.go_to_previous_page)
        # Añadir icono
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
        # Añadir icono
        icon_next = QApplication.style().standardIcon(QApplication.style().StandardPixmap.SP_ArrowForward)
        self.next_button.setIcon(icon_next)
        layout.addWidget(self.next_button)
        
        layout.addStretch() # Empujar controles a la izquierda si se desea, o centrar.
                            # Para centrar, añadir stretch a ambos lados.
        
        main_layout.addWidget(pagination_container)

    def go_to_previous_page(self):
        """Navegar a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            self.page_changed_requested.emit(self.current_page)

    def go_to_next_page(self):
        """Navegar a la página siguiente."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_changed_requested.emit(self.current_page)

    def update_pagination_controls(self):
        """Actualizar el estado de los botones y la etiqueta de paginación."""
        self.page_label.setText(f"Página {self.current_page} de {self.total_pages}")
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        
    def update_filters(self, stats: dict):
        """
        Actualizar opciones de filtros
        
        Args:
            stats: Diccionario con estadísticas {
                'artists': list,
                'genres': list
            }
        """
        self.artist_combo.clear()
        self.artist_combo.addItem("Todos los artistas")
        self.artist_combo.addItems(sorted(stats['artists']))
        
        self.genre_combo.clear()
        self.genre_combo.addItem("Todos los géneros")
        self.genre_combo.addItems(sorted(stats['genres']))
        
    def on_search_changed(self):
        """Activar debouncing para emitir señal de búsqueda."""
        # Detener el timer anterior si estaba corriendo
        self._search_timer.stop()
        # Iniciar nuevo timer con delay
        self._search_timer.start(self._search_debounce_delay)
    
    def _emit_search_changed(self):
        """Emitir señal de búsqueda con filtros actuales y resetear a página 1."""
        self.current_page = 1 # Resetear a la primera página en nueva búsqueda
        title = self.search_field.text()
        
        artist = self.artist_combo.currentText()
        if artist == "Todos los artistas":
            artist = ""
            
        genre = self.genre_combo.currentText()
        if genre == "Todos los géneros":
            genre = ""
            
        self.search_changed.emit(title, artist, genre)
        
    def load_songs(self, songs: list, total_items: int = None):
        """Cargar canciones en la tabla y actualizar paginación."""
        self.table.load_songs(songs) # Pasar solo la lista de canciones
        
        if total_items is not None:
            if total_items == 0:
                self.total_pages = 1 # Evitar división por cero si no hay items
                self.current_page = 1
            else:
                self.total_pages = (total_items + self.items_per_page - 1) // self.items_per_page
        else:
            # Si no se provee total_items, asumimos una sola página con las canciones dadas
            self.total_pages = 1
            self.current_page = 1
            
        self.update_pagination_controls()
        
    def clear(self):
        """Limpiar vista"""
        self.search_field.clear()
        self.artist_combo.setCurrentIndex(0)
        self.genre_combo.setCurrentIndex(0)
        self.table.clear()
        
    def on_scale_changed(self, scale_factor: float):
        """Manejar cambio de escala"""
        margin = int(24 * scale_factor)
        spacing = int(16 * scale_factor)
        
        self.layout().setContentsMargins(margin, margin, margin, margin)
        self.layout().setSpacing(spacing)
        
    def on_theme_changed(self, is_dark: bool):
        """Manejar cambio de tema"""
        pass
        
    def refresh(self):
        """Actualizar vista"""
        if hasattr(self.table, 'table') and self.table.table is not None:
            self.table.table.viewport().update()
        else:
            print("[LibraryView] Advertencia: self.table.table no disponible para refresh.")
            self.table.update()
        
    def cleanup(self):
        """Limpiar recursos"""
        self.table.clear()
        self.clear()
