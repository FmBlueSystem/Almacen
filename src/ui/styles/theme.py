"""
Sistema de estilos Material Design 3
"""

from .color_scheme import get_theme_colors

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
            * {{
                color: {colors["on-surface"]};
                background-color: {colors["surface"]};
                selection-background-color: {colors["primary-container"]};
                selection-color: {colors["on-primary-container"]};
                font-family: Arial;
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
                min-width: 280px;
                max-width: 280px;
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
                padding: 12px;
            }}

            QPushButton#playbackButton {{
                background-color: transparent;
                border: 1px solid {colors["outline"]};
                border-radius: 20px;
                padding: 8px;
                margin: 0 4px;
                min-width: 40px;
                max-width: 40px;
                min-height: 40px;
                max-height: 40px;
            }}

            QPushButton#playbackButton:disabled {{
                color: {colors["outline"]};
                border-color: {colors["outline-variant"]};
            }}

            QPushButton#playButton {{
                background-color: {colors["primary-container"]};
                color: {colors["on-primary-container"]};
                border: none;
                border-radius: 24px;
                padding: 12px;
                margin: 0 8px;
                min-width: 48px;
                max-width: 48px;
                min-height: 48px;
                max-height: 48px;
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

            QSlider#progressSlider::handle:horizontal {{
                background: {colors["primary"]};
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }}

            /* Tablas */
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
            
            /* Botones MD3 */
            QPushButton#primaryButton {{
                background-color: {colors["primary"]};
                color: {colors["on-primary"]};
                border: none;
                border-radius: 20px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
            }}
            
            QPushButton#primaryButton:hover {{
                background-color: {colors["primary"]}ee;
            }}
            
            QPushButton#primaryButton:pressed {{
                background-color: {colors["primary"]}cc;
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
            
            /* Campos de búsqueda */
            QLineEdit#searchField {{
                background-color: {colors["surface-variant"]};
                color: {colors["on-surface-variant"]};
                border: none;
                border-radius: 24px;
                padding: 12px 24px;
                font-size: 16px;
            }}
            
            QLineEdit#searchField:focus {{
                background-color: {colors["primary-container"]};
                color: {colors["on-primary-container"]};
            }}
            
            /* Combo boxes */
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
            
            /* Contenedores */
            QFrame#contentContainer {{
                background-color: {colors["surface"]};
                border-radius: 28px;
                padding: 24px;
            }}
            
            /* Headers */
            QLabel#sectionTitle {{
                color: {colors["on-surface"]};
                font-weight: 600;
                font-size: 24px;
                margin-bottom: 16px;
            }}
            
            /* Tablas */
            QTableWidget#dataTable {{
                background-color: {colors["surface"]};
                border: 1px solid {colors["outline"]};
                border-radius: 16px;
                padding: 1px;
                gridline-color: {colors["outline-variant"]};
            }}

            QHeaderView::section {{
                background-color: {colors["surface-variant"]};
                color: {colors["on-surface-variant"]};
                padding: 12px;
                border: none;
                border-right: 1px solid {colors["outline"]};
                border-bottom: 1px solid {colors["outline"]};
                font-weight: 500;
            }}

            QHeaderView::section:first {{
                border-top-left-radius: 15px;
            }}

            QHeaderView::section:last {{
                border-top-right-radius: 15px;
                border-right: none;
            }}

            QHeaderView::section:hover {{
                background-color: {colors["secondary-container"]};
                color: {colors["on-secondary-container"]};
            }}
            
            QTableWidget#dataTable::item {{
                padding: 12px;
            }}
            
            QTableWidget#dataTable::item:selected {{
                background-color: {colors["secondary-container"]};
                color: {colors["on-secondary-container"]};
            }}
            
            /* Sliders */
            QSlider::groove:horizontal {{
                background: {colors["surface-variant"]};
                height: 4px;
                border-radius: 2px;
            }}
            
            QSlider::handle:horizontal {{
                background: {colors["primary"]};
                width: 20px;
                margin: -8px 0;
                border-radius: 10px;
            }}
            
            /* Scroll bars */
            QScrollBar:vertical {{
                background: {colors["surface-variant"]};
                width: 10px;
                margin: 0;
                border-radius: 5px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {colors["primary-container"]};
                min-height: 20px;
                border-radius: 5px;
            }}
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
                height: 0;
            }}
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {{
                background: none;
                border: none;
            }}
        """
    
    @staticmethod
    def get_fonts() -> dict:
        """Obtener definiciones de fuentes MD3"""
        default_font = "Arial"
        return {
            "display-large": f"{default_font} 57px",
            "display-medium": f"{default_font} 45px",
            "display-small": f"{default_font} 36px",
            "headline-large": f"{default_font} 32px",
            "headline-medium": f"{default_font} 28px",
            "headline-small": f"{default_font} 24px",
            "title-large": f"{default_font} 22px",
            "title-medium": f"{default_font} 16px",
            "title-small": f"{default_font} 14px",
            "body-large": f"{default_font} 16px",
            "body-medium": f"{default_font} 14px",
            "body-small": f"{default_font} 12px",
            "label-large": f"{default_font} 14px",
            "label-medium": f"{default_font} 12px",
            "label-small": f"{default_font} 11px"
        }
