"""
Ventana principal con Material Design 3
"""

import traceback
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout,
    QHBoxLayout, QStackedWidget, QMenuBar,
    QMenu, QStatusBar, QApplication, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QSize, QEvent
from PyQt6.QtGui import QAction, QFontDatabase, QResizeEvent

from ..styles.theme import MD3Theme
from ..styles.color_scheme import get_theme_colors
from ..config import UIConfig
from ..components.navigation_rail import NavigationRail
from ..components.playback_panel import PlaybackPanel
from ..components.content_views.library_view import LibraryView
from ..components.content_views.playlist_view import PlaylistView
from ..components.content_views.settings_view import SettingsView
from src.services.music_service import MusicService
from src.services.audio_service import AudioService
from src.database.connection import DatabaseConnection
from src.views.base_view import BaseView



class MainWindow(QMainWindow):
    """Ventana principal de la aplicación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Servicios
        self.db = DatabaseConnection()
        self.music_service = MusicService(self.db)
        self.audio_service = AudioService(self)
        
        # Estado
        self.current_scale = 1.0
        self._force_exit = False  # Flag para control de salida
        
        print("[MainWindow] Iniciando configuración...")
        self.init_ui()
        self.setup_theme()
        
        # Establecer tamaño inicial
        self.resize(1280, 720)
        self.show()
        
        print("[MainWindow] Configuración completada.")
        # No cargar datos inicialmente para evitar problemas de reproducción automática
        # Los datos se cargarán cuando el usuario interactúe con la interfaz
        
    def init_ui(self):
        """Inicializar interfaz"""
        self.setWindowTitle("Almacena - Sistema de Gestión")
        
        # Establecer dimensiones base
        width, height = UIConfig.get_base_resolution()
        self.setMinimumSize(width // 2, height // 2)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Crear componentes principales
        self.create_menu_bar()
        self.setup_main_layout()
        self.create_status_bar()
        
    def setup_main_layout(self):
        """Configurar layout principal"""
        # Container principal
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation Rail
        self.nav_rail = NavigationRail()
        self.nav_rail.navigation_changed.connect(self.on_navigation_changed)
        layout.addWidget(self.nav_rail)
        
        # Área de contenido
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Stack de contenido
        self.content_stack = QStackedWidget()
        
        # Vistas principales
        # Vista de biblioteca
        self.library_view = LibraryView(audio_service=self.audio_service)
        self.library_view.search_changed.connect(self.on_search_changed)
        self.library_view.song_selection_changed.connect(self.on_song_selection_changed)
        self.library_view.song_double_clicked.connect(self.on_song_double_clicked)
        self.content_stack.addWidget(self.library_view)
        
        self.playlist_view = PlaylistView()
        self.content_stack.addWidget(self.playlist_view)
        
        self.settings_view = SettingsView()
        self.content_stack.addWidget(self.settings_view)
        
        content_layout.addWidget(self.content_stack)
        
        # Panel de reproducción
        self.playback_panel = PlaybackPanel()
        self.connect_playback_panel_signals()
        content_layout.addWidget(self.playback_panel)
        
        layout.addWidget(content_area)
        
        # Splitter para redimensionamiento
        layout.setStretch(0, 1)  # Navigation rail
        layout.setStretch(1, 4)  # Contenido
        
        # Agregar al layout central
        self.centralWidget().layout().addWidget(container)
        
    def connect_playback_panel_signals(self):
        """Conectar señales entre AudioService y PlaybackPanel."""
        if not self.audio_service or not self.playback_panel:
            return

        # Conectar acciones de PlaybackPanel a AudioService
        # Conectar controles básicos
        self.playback_panel.play_requested.connect(self.audio_service.resume)
        self.playback_panel.pause_requested.connect(self.audio_service.pause)
        self.playback_panel.seek_requested.connect(self.audio_service.seek)
        self.playback_panel.volume_change_requested.connect(self.audio_service.set_volume)
        
        # Conectar controles de navegación
        self.playback_panel.previous_requested.connect(self.audio_service.play_previous)
        self.playback_panel.next_requested.connect(self.audio_service.play_next)

        # Conectar señales de AudioService a slots de PlaybackPanel
        # Conectar señales de estado
        self.audio_service.playback_state_changed.connect(self.playback_panel.update_playback_state)
        self.audio_service.song_progress_updated.connect(self.playback_panel.update_progress)
        self.audio_service.current_song_changed.connect(self.playback_panel.update_current_song)
        
        # Conectar señales de navegación
        self.audio_service.previous_available.connect(self.playback_panel.prev_button.setEnabled)
        self.audio_service.next_available.connect(self.playback_panel.next_button.setEnabled)
        
        # Conectar error de audio a la status bar
        self.audio_service.error_occurred.connect(self.show_audio_error)
        
    def create_menu_bar(self):
        """Crear barra de menú"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        import_menu = file_menu.addMenu("&Importar")
        
        folder_action = QAction("&Carpeta", self)
        folder_action.setShortcut("Ctrl+Shift+O")
        folder_action.triggered.connect(self.import_folder)
        import_menu.addAction(folder_action)
        
        files_action = QAction("&Archivos", self)
        files_action.setShortcut("Ctrl+O")
        files_action.triggered.connect(self.import_files)
        import_menu.addAction(files_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("&Salir", self)
        self.exit_action.setShortcut("Ctrl+Q")
        self.exit_action.triggered.connect(self._handle_exit)
        file_menu.addAction(self.exit_action)
        
        # Menú Ver
        view_menu = menubar.addMenu("&Ver")
        
        theme_menu = view_menu.addMenu("&Tema")
        
        light_action = QAction("&Claro", self)
        light_action.setCheckable(True)
        light_action.setChecked(not UIConfig.is_dark_theme())
        light_action.toggled.connect(self.on_theme_changed)
        theme_menu.addAction(light_action)
        
        dark_action = QAction("&Oscuro", self)
        dark_action.setCheckable(True)
        dark_action.setChecked(UIConfig.is_dark_theme())
        theme_menu.addAction(dark_action)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("&Ayuda")
        
        about_action = QAction("&Acerca de", self)
        help_menu.addAction(about_action)
        
    def create_status_bar(self):
        """Crear barra de estado"""
        status_bar = QStatusBar()
        status_bar.showMessage("Listo")
        self.setStatusBar(status_bar)
        
    def setup_theme(self):
        """Configurar tema Material Design 3"""
        is_dark = UIConfig.is_dark_theme()
        colors = get_theme_colors(is_dark)
        self.setStyleSheet(MD3Theme.get_stylesheet(colors=colors, is_dark=is_dark))
        
        # Cargar fuente
        font_path = UIConfig.FONT_PATH
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            else:
                font_family = UIConfig.FONT_FAMILY
        else:
            font_family = UIConfig.FONT_FAMILY
            
        # Aplicar fuente a la aplicación
        app = QApplication.instance()
        if app:
            current_font = app.font()
            current_font.setFamily(font_family)
            app.setFont(current_font)
    
    def update_library_filters_and_songs(self):
        """Actualiza los filtros y las canciones en la vista de la biblioteca."""
        try:
            # Obtener estadísticas actualizadas
            all_songs_data, _ = self.music_service.get_songs(page=1, per_page=10000) # Obtener todas las canciones para stats
            stats = {
                'total_songs': len(all_songs_data),
                'artists': sorted(list(set(song.artist for song in all_songs_data if song.artist))),
                'genres': sorted(list(set(song.genre for song in all_songs_data if song.genre))),
                'years': []  # TODO: Implementar años
            }
            self.library_view.update_filters(stats)

            # Cargar/Recargar canciones en la vista (podría ser paginado)
            songs_to_display, total_songs_for_view = self.music_service.get_songs(page=1, per_page=50) # Carga inicial paginada
            self.library_view.load_songs(songs_to_display, total_songs_for_view)
            
            # Actualizar navegación (si es necesario)
            self.nav_rail.update_library_stats(stats)

        except Exception as e:
            self.statusBar().showMessage(f"Error actualizando la biblioteca: {e}", 5000)
            QMessageBox.critical(self, "Error de Biblioteca", f"No se pudo actualizar la biblioteca: {e}")

    def load_library_data(self):
        """Cargar datos iniciales"""
        try:
            # Obtener estadísticas
            stats = {
                'total_songs': len(self.music_service.get_songs(1, 1000)[0]),
                'artists': list(set(song.artist for song in self.music_service.get_songs(1, 1000)[0])),
                'genres': list(set(song.genre for song in self.music_service.get_songs(1, 1000)[0] if song.genre)),
                'years': []  # TODO: Implementar años
            }
            
            # Actualizar navegación
            self.nav_rail.update_library_stats(stats)
            
            # Actualizar filtros de biblioteca
            self.library_view.update_filters(stats)
            
            # Cargar canciones
            songs, total_pages = self.music_service.get_songs(1, 50)
            self.library_view.load_songs(songs, len(songs))
            
        except Exception as e:
            self.statusBar().showMessage(f"Error cargando biblioteca: {e}")
            
    def on_navigation_changed(self, section: str, item: str):
        """Manejar cambio de navegación"""
        if section == "library":
            # Cargar datos solo cuando se navega a la biblioteca por primera vez
            if not hasattr(self, '_library_loaded'):
                print("[MainWindow] Cargando datos de biblioteca...")
                self.load_library_data()
                self._library_loaded = True
            self.content_stack.setCurrentWidget(self.library_view)
        elif section == "playlists":
            self.content_stack.setCurrentWidget(self.playlist_view)
        elif section == "settings":
            self.content_stack.setCurrentWidget(self.settings_view)
            
    def on_search_changed(self, title: str, artist: str, genre: str):
        """Manejar cambio en filtros de búsqueda"""
        try:
            if title or artist or genre:
                songs, _ = self.music_service.search_songs(
                    title, artist, genre, 1, 50
                )
            else:
                songs, _ = self.music_service.get_songs(1, 50)
                
            self.library_view.load_songs(songs, len(songs))
            self.statusBar().showMessage(f"Mostrando {len(songs)} canciones")
            
        except Exception as e:
            self.statusBar().showMessage(f"Error en búsqueda: {e}")
            
    def on_song_selection_changed(self, selected_songs: list[dict], selected_index: int):
        """
        Manejar cambio en la selección de canciones.
        Actualiza la lista de reproducción con las canciones disponibles.
        """
        if not selected_songs:
            return
            
        self.audio_service.set_playlist(selected_songs, selected_index)
        
    def on_song_double_clicked(self, song_data: dict):
        """
        Manejar doble clic en una canción.
        Reproduce la canción seleccionada.
        """
        if song_data:
            self.audio_service.play_song(song_data)
        
    def on_theme_changed(self, use_light: bool):
        """Cambiar tema de la aplicación"""
        UIConfig.set_dark_theme(not use_light)
        self.setup_theme()
        # Actualizar componentes
        self.nav_rail.update_theme()
        self.library_view.update_theme()
        self.playlist_view.update_theme()
        self.settings_view.update_theme()
        self.playback_panel.update_theme()
        
    def import_folder(self):
        """Importar carpeta de música"""
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Música", "")
        if folder_path:
            try:
                imported, failed = self.music_service.import_folder(folder_path)
                self.statusBar().showMessage(f"{imported} canciones importadas, {failed} fallaron.", 5000)
                # Actualizar la vista de la biblioteca después de la importación
                self.update_library_filters_and_songs()
            except FileNotFoundError as e:
                QMessageBox.warning(self, "Error", str(e))
                self.statusBar().showMessage(f"Error al importar: {e}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Ocurrió un error inesperado: {e}")
                self.statusBar().showMessage(f"Error inesperado al importar: {e}", 5000)
        
    def import_files(self):
        """Importar archivos de música"""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Seleccionar Archivos de Música",
            "",
            "Archivos de Audio (*.mp3 *.wav *.m4a *.flac);;Todos los archivos (*.*)"
        )
        
        if file_paths:
            try:
                imported, failed = self.music_service.import_files(file_paths)
                
                self.statusBar().showMessage(
                    f"{imported} archivos importados, {failed} fallaron.",
                    5000
                )
                
                # Actualizar la vista de la biblioteca
                self.update_library_filters_and_songs()
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error importando archivos: {e}"
                )
                self.statusBar().showMessage(f"Error en importación: {e}", 5000)
        
    def resizeEvent(self, event: QResizeEvent):
        """Manejar cambio de tamaño de la ventana"""
        super().resizeEvent(event)
        
        # Calcular nueva escala
        width = event.size().width()
        height = event.size().height()
        self.current_scale = UIConfig.get_scale_factor(width, height)
        
        # Actualizar tamaños de componentes
        self.update_component_sizes()
        
    def update_component_sizes(self):
        """Actualizar tamaños de componentes según escala"""
        # Navigation rail
        nav_width = UIConfig.scale_size(280, self.width(), self.height())
        self.nav_rail.setFixedWidth(nav_width)
        
        # Ajustes de tamaño para otros componentes
        self.playback_panel.setFixedHeight(UIConfig.scale_size(100, self.width(), self.height()))
        
        # Ajustar tamaños de texto
        font_size = UIConfig.scale_size(12, self.width(), self.height())
        app = QApplication.instance()
        if app:
            font = app.font()
            font.setPointSize(font_size)
            app.setFont(font)

    def show_audio_error(self, error_message: str):
        """Muestra un mensaje de error de audio en la barra de estado."""
        self.statusBar().showMessage(f"Error de audio: {error_message}", 7000)

    def _handle_exit(self):
        """Manejador para la acción de salir del menú"""
        print("[MainWindow] Saliendo por acción del menú...")
        self._force_exit = True  # Marcar que es una salida intencional
        self.close()  # Esto disparará el closeEvent
        
    def closeEvent(self, event):
        """Manejar evento de cierre para limpiar servicios."""
        print("[MainWindow] closeEvent recibido")
        print("[MainWindow] Es cierre forzado:", self._force_exit)
        
        if not self._force_exit:
            # Si no es un cierre forzado, mostrar diálogo de confirmación
            reply = QMessageBox.question(
                self,
                "Confirmar salida",
                "¿Está seguro que desea salir de la aplicación?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.No:
                print("[MainWindow] Cancelando cierre por usuario...")
                event.ignore()
                self._force_exit = False
                return
            else:
                print("[MainWindow] Usuario confirmó el cierre")
                self._force_exit = True
                
        # Proceder con el cierre solo si está marcado como forzado
        if self._force_exit:
            print("[MainWindow] Cerrando aplicación...")
            if hasattr(self, 'audio_service') and self.audio_service:
                self.audio_service.cleanup()
            event.accept()
        else:
            print("[MainWindow] Ignorando cierre no autorizado")
            event.ignore()
