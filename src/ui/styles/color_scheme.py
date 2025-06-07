"""
Sistema de colores Material Design 3
"""

class MD3LightColors:
    """Paleta de colores Material Design 3 - Tema Claro"""
    # Colores primarios
    PRIMARY = "#6200EE"
    ON_PRIMARY = "#ffffff"
    PRIMARY_CONTAINER = "#E8DEF8"
    ON_PRIMARY_CONTAINER = "#21005E"
    
    # Colores secundarios
    SECONDARY = "#03DAC6"
    ON_SECONDARY = "#000000"
    SECONDARY_CONTAINER = "#CEFAF3"
    ON_SECONDARY_CONTAINER = "#00504D"
    
    # Colores de superficie
    SURFACE = "#FAFAFA"
    ON_SURFACE = "#1C1B1F"
    SURFACE_VARIANT = "#E7E0EC"
    ON_SURFACE_VARIANT = "#49454F"
    SURFACE_TINT = "#6200EE"
    
    # Colores de utilidad
    OUTLINE = "#79747e"
    OUTLINE_VARIANT = "#cac4d0"
    SHADOW = "rgba(0, 0, 0, 0.15)"
    SCRIM = "rgba(0, 0, 0, 0.3)"
    INVERSE_SURFACE = "#313033"
    INVERSE_ON_SURFACE = "#f4eff4"
    
    # Colores de estado
    ERROR = "#B00020"
    ON_ERROR = "#FFFFFF"
    ERROR_CONTAINER = "#FFDAD9"
    ON_ERROR_CONTAINER = "#410002"
    
    # Colores de éxito
    SUCCESS = "#00C853"
    ON_SUCCESS = "#FFFFFF"
    SUCCESS_CONTAINER = "#D7F8D7"
    ON_SUCCESS_CONTAINER = "#005C26"
    
    # Colores informativos
    INFO = "#2196F3"
    ON_INFO = "#FFFFFF"
    INFO_CONTAINER = "#E3F2FD"
    ON_INFO_CONTAINER = "#0D47A1"
    
    # Colores de advertencia
    WARNING = "#FFB300"
    ON_WARNING = "#000000"
    WARNING_CONTAINER = "#FFF3E0"
    ON_WARNING_CONTAINER = "#7A5700"

class MD3DarkColors:
    """Paleta de colores Material Design 3 - Tema Oscuro"""
    # Colores primarios
    PRIMARY = "#d0bcff"
    ON_PRIMARY = "#381e72"
    PRIMARY_CONTAINER = "#4f378b"
    ON_PRIMARY_CONTAINER = "#eaddff"
    
    # Colores secundarios
    SECONDARY = "#ccc2dc"
    ON_SECONDARY = "#332d41"
    SECONDARY_CONTAINER = "#4a4458"
    ON_SECONDARY_CONTAINER = "#e8def8"
    
    # Colores de superficie
    SURFACE = "#1c1b1f"
    ON_SURFACE = "#e6e1e5"
    SURFACE_VARIANT = "#49454f"
    ON_SURFACE_VARIANT = "#cac4d0"
    SURFACE_TINT = "#d0bcff"
    
    # Colores de utilidad
    OUTLINE = "#938f99"
    OUTLINE_VARIANT = "#49454f"
    SHADOW = "rgba(0, 0, 0, 0.3)"
    SCRIM = "rgba(0, 0, 0, 0.6)"
    INVERSE_SURFACE = "#e6e1e5"
    INVERSE_ON_SURFACE = "#313033"
    
    # Colores de estado
    ERROR = "#f2b8b5"
    ON_ERROR = "#601410"
    ERROR_CONTAINER = "#8c1d18"
    ON_ERROR_CONTAINER = "#f9dedc"

# Para mantener compatibilidad con código existente
MD3Colors = MD3LightColors
    
def get_theme_colors(is_dark: bool = False) -> dict:
    """
    Obtener colores del tema actual
    
    Args:
        is_dark: Si es True, devuelve colores del tema oscuro
        
    Returns:
        dict: Diccionario con los colores del tema
    """
    ColorScheme = MD3DarkColors if is_dark else MD3LightColors
    return {
        "primary": ColorScheme.PRIMARY,
        "on-primary": ColorScheme.ON_PRIMARY,
        "primary-container": ColorScheme.PRIMARY_CONTAINER,
        "on-primary-container": ColorScheme.ON_PRIMARY_CONTAINER,
        "secondary": ColorScheme.SECONDARY,
        "on-secondary": ColorScheme.ON_SECONDARY,
        "secondary-container": ColorScheme.SECONDARY_CONTAINER,
        "on-secondary-container": ColorScheme.ON_SECONDARY_CONTAINER,
        "surface": ColorScheme.SURFACE,
        "on-surface": ColorScheme.ON_SURFACE,
        "surface-variant": ColorScheme.SURFACE_VARIANT,
        "on-surface-variant": ColorScheme.ON_SURFACE_VARIANT,
        "surface-tint": ColorScheme.SURFACE_TINT,
        "outline": ColorScheme.OUTLINE,
        "outline-variant": ColorScheme.OUTLINE_VARIANT,
        "shadow": ColorScheme.SHADOW,
        "scrim": ColorScheme.SCRIM,
        "inverse-surface": ColorScheme.INVERSE_SURFACE,
        "inverse-on-surface": ColorScheme.INVERSE_ON_SURFACE,
        "error": ColorScheme.ERROR,
        "on-error": ColorScheme.ON_ERROR,
        "error-container": ColorScheme.ERROR_CONTAINER,
        "on-error-container": ColorScheme.ON_ERROR_CONTAINER
    }
