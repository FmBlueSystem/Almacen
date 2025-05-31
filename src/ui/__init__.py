"""
Interfaz de usuario con Material Design 3
"""

from .windows import MainWindow
from .components import (
    NavigationRail,
    PlaybackPanel,
    SongTable,
    LibraryView,
    PlaylistView,
    SettingsView
)

__all__ = [
    'MainWindow',
    'NavigationRail',
    'PlaybackPanel',
    'SongTable',
    'LibraryView',
    'PlaylistView',
    'SettingsView'
]
