"""
Sistema de estilos Material Design 3
"""

# Implements Dart AI Task: Refactor theme module

from .color_scheme import get_theme_colors
from .typography import get_fonts as typography_fonts

class MD3Theme:
    """Sistema de estilos Material Design 3"""
    _is_dark = False

    @classmethod
    def set_dark_mode(cls, is_dark: bool):
        """Cambiar entre tema claro y oscuro"""
        cls._is_dark = is_dark

    @classmethod
    def is_dark_mode(cls) -> bool:
        """Obtener el modo actual"""
        return cls._is_dark
    
    @staticmethod
    def _get_ripple_animation() -> str:
        """Obtener animación de ripple effect"""
        return """
        /* Ripple effect */
        @keyframes ripple {
            0% { 
                background-color: rgba(0, 0, 0, 0);
                transform: scale(0); 
            }
            50% { 
                transform: scale(1.5); 
            }
            100% { 
                background-color: rgba(0, 0, 0, 0.1);
                transform: scale(2); 
            }
        }
        """
    
    @staticmethod
    def get_stylesheet(colors: dict = None, is_dark: bool = None) -> str:
        """
        Obtener hoja de estilos QSS con colores Material Design 3
        
        Args:
            colors: Diccionario de colores (opcional, usa MD3Colors por defecto)
        
        Returns:
            str: Stylesheet QSS
        """
        if colors is None:
            colors = get_theme_colors(is_dark if is_dark is not None else MD3Theme._is_dark)
            
        return f"""
            /* Reset global styles */
            @font-face {{
                font-family: "Roboto Flex";
                src: url("assets/fonts/RobotoFlex-Regular.ttf");
            }}
            
            * {{
                color: {colors["on-surface"]};
                background-color: {colors["surface"]};
                selection-background-color: {colors["primary-container"]};
                selection-color: {colors["on-primary-container"]};
                font-family: "Roboto Flex", Arial;
            }}
            
            /* Animaciones */
            {MD3Theme._get_ripple_animation()}
            
            /* Transiciones globales */
            * {{
                transition: background-color 0.2s ease,
                            color 0.2s ease,
                            border-color 0.2s ease,
                            box-shadow 0.2s ease;
            }}

            /* Estilos globales MD3 */
            QMainWindow {{
                background-color: {colors["surface"]};
                color: {colors["on-surface"]};
            }}
            
            /* NavigationRail */
            QFrame#navigationRail {{
                background-color: {colors["surface-variant"]};
                border-right: 1px solid {colors["outline"]};
                min-width: 72px;
                max-width: 72px;
            }}
            
            QFrame#navigationRail[expanded="true"] {{
                min-width: 256px;
                max-width: 256px;
            }}
            
            QFrame#appHeader {{
                padding: 24px 16px;
                border-bottom: 1px solid {colors["outline"]};
            }}
            
            QLabel#appTitle {{
                color: {colors["primary"]};
                font-weight: 600;
                font-size: 20px;
            }}
            
            /* Panel de reproducción */
            QFrame#playbackPanel {{
                background-color: {colors["surface-variant"]};
                border-top: 1px solid {colors["outline"]};
                padding: 16px 24px;
            }}

            /* Información de canción */
            QLabel#playingTitle {{
                color: {colors["on-surface"]};
                font-size: 16px;
                font-weight: 600;
            }}

            QLabel#playingArtist {{
                color: {colors["on-surface-variant"]};
                font-size: 14px;
            }}

            QLabel#timeLabel {{
                color: {colors["on-surface-variant"]};
                font-size: 12px;
                min-width: 45px;
            }}

            /* Controles de reproducción */
            QPushButton#playbackButton {{
                background-color: {colors["surface"]};
                color: {colors["on-surface"]};
                border: 1px solid {colors["outline"]};
                border-radius: 20px;
                padding: 8px;
                margin: 0 4px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
                font-size: 16px;
            }}

            QPushButton#playbackButton:hover {{
                background-color: {colors["primary-container"]};
                color: {colors["on-primary-container"]};
                border-color: {colors["primary"]};
            }}

            QPushButton#playbackButton:pressed {{
                background-color: {colors["primary"]};
                color: {colors["on-primary"]};
            }}

            QPushButton#playbackButton:disabled {{
                color: {colors["outline"]};
                border-color: {colors["outline-variant"]};
                background-color: {colors["surface-variant"]};
            }}

            QPushButton#playbackButton:checked {{
                background-color: {colors["primary-container"]};
                color: {colors["on-primary-container"]};
                border-color: {colors["primary"]};
            }}

            QPushButton#playButton {{
                background-color: {colors["primary"]};
                color: {colors["on-primary"]};
                border: none;
                border-radius: 24px;
                padding: 12px;
                margin: 0 8px;
                min-width: 48px;
                max-width: 48px;
                min-height: 48px;
                max-height: 48px;
                font-size: 20px;
            }}

            QPushButton#playButton:hover {{
                background-color: {colors["primary-container"]};
                color: {colors["on-primary-container"]};
            }}

            QPushButton#playButton:disabled {{
                background-color: {colors["surface-variant"]};
                color: {colors["outline"]};
            }}

            /* Barra de progreso */
            QSlider#progressSlider {{
                height: 24px;
            }}

            QSlider#progressSlider::groove:horizontal {{
                background: {colors["surface-variant"]};
                height: 4px;
                border-radius: 2px;
            }}

            QSlider#progressSlider::sub-page:horizontal {{
                background: {colors["primary"]};
                height: 4px;
                border-radius: 2px;
            }}

            QSlider#progressSlider::handle:horizontal {{
                background: {colors["primary"]};
                border: 2px solid {colors["on-primary"]};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}

            QSlider#progressSlider::handle:horizontal:hover {{
                background: {colors["primary-container"]};
                border-color: {colors["primary"]};
            }}

            /* Control de volumen */
            QLabel#volumeIcon {{
                color: {colors["on-surface-variant"]};
                font-size: 16px;
                padding: 0 8px;
            }}

            QSlider#volumeSlider {{
                height: 24px;
                max-width: 100px;
            }}

            QSlider#volumeSlider::groove:horizontal {{
                background: {colors["surface-variant"]};
                height: 4px;
                border-radius: 2px;
            }}

            QSlider#volumeSlider::sub-page:horizontal {{
                background: {colors["secondary"]};
                height: 4px;
                border-radius: 2px;
            }}

            QSlider#volumeSlider::handle:horizontal {{
                background: {colors["secondary"]};
                border: 2px solid {colors["on-secondary"]};
                width: 16px;
                height: 16px;
                margin: -6px 0;
                border-radius: 8px;
            }}

            QSlider#volumeSlider::handle:horizontal:hover {{
                background: {colors["secondary-container"]};
                border-color: {colors["secondary"]};
            }}

            /* Tablas y otros componentes heredados */
            QTreeWidget#navigationTree {{
                background-color: transparent;
                border: none;
                outline: none;
                padding: 8px;
            }}
            
            QTreeWidget#navigationTree::item {{
                padding: 12px 16px;
                border-radius: 100px;
                margin: 2px 8px;
            }}
            
            QTreeWidget#navigationTree::item:selected {{
                background-color: {colors["secondary-container"]};
                color: {colors["on-secondary-container"]};
            }}
            
            QTreeWidget#navigationTree::item:hover:!selected {{
                background-color: {colors["surface-variant"]};
            }}
            
            QPushButton#primaryButton {{
                background-color: {colors["primary"]};
                color: {colors["on-primary"]};
                border: none;
                border-radius: 24px;
                padding: 12px 24px;
                font-weight: 500;
                font-size: 14px;
                min-height: 48px;
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {colors["primary"]};
                box-shadow: 0 2px 4px {colors["shadow"]};
                transform: translateY(-1px);
            }}
            
            QPushButton#primaryButton:pressed {{
                background-color: {colors["primary"]};
                transform: scale(0.98);
                box-shadow: 0 1px 2px {colors["shadow"]};
            }}
            
            QPushButton#primaryButton:focus {{
                outline: 2px solid {colors["primary-container"]};
                outline-offset: 2px;
            }}
            
            QPushButton#primaryButton:disabled {{
                background-color: {colors["surface-variant"]};
                color: {colors["outline"]};
                box-shadow: none;
            }}
            
            QPushButton#secondaryButton {{
                background-color: {colors["secondary-container"]};
                color: {colors["on-secondary-container"]};
                border: none;
                border-radius: 20px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
            }}
            
            QLineEdit#searchField {{
                background-color: {colors["surface-variant"]};
                color: {colors["on-surface-variant"]};
                border: 2px solid transparent;
                border-radius: 24px;
                padding: 12px 24px;
                font-size: 16px;
                min-height: 48px;
            }}
            
            QLineEdit#searchField:hover {{
                background-color: {colors["surface-variant"]};
                border-color: {colors["outline-variant"]};
            }}
            
            QLineEdit#searchField:focus {{
                background-color: {colors["surface"]};
                border-color: {colors["primary"]};
                color: {colors["on-surface"]};
                box-shadow: 0 2px 4px {colors["shadow"]};
            }}
            
            QComboBox#filterCombo {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["outline"]};
                border-radius: 12px;
                padding: 8px 16px;
                min-width: 120px;
            }}
            
            QComboBox#filterCombo:hover {{
                border-color: {colors["primary"]};
            }}
            
            QFrame#contentContainer {{
                background-color: {colors["surface"]};
                border-radius: 28px;
                padding: 24px;
            }}
            
            QLabel#sectionTitle {{
                color: {colors["on-surface"]};
                font-weight: 600;
                font-size: 24px;
                margin-bottom: 16px;
            }}
            
            QTableWidget#dataTable {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["outline"]};
                border-radius: 16px;
                padding: 1px;
                gridline-color: {colors["outline-variant"]};
            }}

            QTableWidget#dataTable QHeaderView::section {{
                background-color: {colors["surface-variant"]};
                color: {colors["on-surface-variant"]};
                padding: 12px;
                border: none;
                border-right: 1px solid {colors["outline"]};
                border-bottom: 1px solid {colors["outline"]};
                font-weight: 500;
            }}

            QTableWidget#dataTable QHeaderView::section:first {{
                border-top-left-radius: 15px;
            }}

            QTableWidget#dataTable QHeaderView::section:last {{
                border-top-right-radius: 15px;
                border-right: none;
            }}

            QTableWidget#dataTable QHeaderView::section:hover {{
                background-color: {colors["surface"]};
            }}
            
            QTableWidget#dataTable::item {{
                padding: 12px;
            }}
            
            QTableWidget#dataTable::item:selected {{
                background-color: {colors["secondary-container"]};
                color: {colors["on-secondary-container"]};
            }}
        """
    
    @staticmethod
    def get_fonts() -> dict:
        """Obtener definiciones de fuentes MD3"""
        # Delegar a módulo separado para reducir tamaño del archivo
        return typography_fonts()
