# Plan de Implementación: Navegación de Audio

## Objetivo
Implementar la funcionalidad de navegación (anterior/siguiente) en el sistema de reproducción de audio.

## Componentes a Modificar

### 1. AudioService

#### Nuevas Señales
```python
# Señales para indicar disponibilidad de navegación
previous_available = pyqtSignal(bool)
next_available = pyqtSignal(bool)
```

#### Nuevos Métodos
```python
def play_previous(self):
    """Reproducir la canción anterior en la lista"""
    # Implementar lógica para obtener y reproducir canción anterior
    pass

def play_next(self):
    """Reproducir la siguiente canción en la lista"""
    # Implementar lógica para obtener y reproducir siguiente canción
    pass

def has_previous(self) -> bool:
    """Verificar si hay una canción anterior disponible"""
    pass

def has_next(self) -> bool:
    """Verificar si hay una siguiente canción disponible"""
    pass
```

### 2. MainWindow

#### Actualizar connect_playback_panel_signals()
```python
# Agregar en connect_playback_panel_signals():
self.playback_panel.previous_requested.connect(self.audio_service.play_previous)
self.playback_panel.next_requested.connect(self.audio_service.play_next)

# Conectar señales de disponibilidad
self.audio_service.previous_available.connect(self.playback_panel.prev_button.setEnabled)
self.audio_service.next_available.connect(self.playback_panel.next_button.setEnabled)
```

## Próximos Pasos

1. Cambiar a modo Code para implementar estos cambios
2. Realizar pruebas de navegación
3. Verificar manejo de errores y casos límite

## Consideraciones Adicionales

- La habilitación/deshabilitación de botones debe reflejar la disponibilidad real de canciones
- Implementar manejo de errores adecuado
- Considerar el comportamiento cuando se llega al final/inicio de la lista