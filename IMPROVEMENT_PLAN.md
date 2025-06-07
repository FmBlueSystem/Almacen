# Plan de Mejoras para "Almacena"

Este documento describe las mejoras prioritarias identificadas para la aplicación "Almacena", centrándose en la robustez, eficiencia y usabilidad del código existente.

## I. Mejoras Críticas (Base de Datos y Servicios)

1.  **Eliminar Creación de Tablas Duplicada:**
    *   **Problema:** `MusicService` (a través de `SongRepository`) intenta crear la tabla `songs` programáticamente. Esto entra en conflicto con el sistema `MigrationManager` (`src/database/migrations.py`).
    *   **Solución:**
        *   Eliminar la llamada a `self.songs.create_table()` del constructor de `MusicService` y cualquier lógica similar de `SongRepository`.
        *   Asegurar que `MigrationManager.run_migrations()` se ejecute al inicio de la aplicación (ej. en `main.py` o un script de inicialización) para que la base de datos se configure exclusivamente mediante migraciones.

## II. Mejoras Importantes (Eficiencia y UX)

1.  **Optimizar Consultas para Filtros de la Interfaz:**
    *   **Problema:** `MainWindow.update_library_filters_and_songs()` carga todas las canciones para extraer listas de artistas/géneros, lo cual es ineficiente.
    *   **Solución:**
        *   Añadir métodos a `SongRepository` (y exponerlos vía `MusicService`) para obtener listas distintas directamente desde la base de datos (ej. `get_distinct_artists()`, `get_distinct_genres()` usando `SELECT DISTINCT`).
        *   Modificar `MainWindow.update_library_filters_and_songs()` para usar estos nuevos métodos.

2.  **Implementar Controles de Paginación en `LibraryView`:**
    *   **Problema:** La `LibraryView` y `SongTable` tienen fundamentos para paginación, pero no hay controles de UI para que el usuario cambie de página.
    *   **Solución:**
        *   Añadir widgets de control de paginación (botones Siguiente/Anterior, indicador de página) a `LibraryView`.
        *   Conectar estos controles para que soliciten la página apropiada de canciones a `MusicService` y actualicen `SongTable`.

3.  **Asegurar Limpieza de Recursos de `AudioService`:**
    *   **Problema:** Es crucial que los recursos de `QMediaPlayer` en `AudioService` se liberen correctamente.
    *   **Solución:**
        *   Verificar y asegurar que se llame a `self.audio_service.cleanup()` en el método `MainWindow.closeEvent()` antes de que la aplicación se cierre.

## III. Mejoras de Mantenimiento y Buenas Prácticas

1.  **Consolidar Configuración:**
    *   **Problema:** Dos archivos de configuración (`src/utils/config.py` y `src/ui/config.py`) con cierta superposición.
    *   **Solución:**
        *   Hacer que `src/utils/config.py` (con su instancia global `config`) sea la única fuente para leer variables de entorno.
        *   Modificar `src/ui/config.py` para que obtenga valores de la instancia `config` global en lugar de leer `os.getenv()` directamente.

2.  **Feedback Visual para Operaciones Largas:**
    *   **Problema:** La importación de música puede ser lenta sin suficiente feedback visual.
    *   **Solución:**
        *   Considerar el uso de `QProgressDialog` o actualizar la `QStatusBar` con más detalle durante la importación en `MainWindow`.
        *   Deshabilitar botones de importación mientras una operación está en curso.

## IV. Revisión Adicional (Post-Mejoras)

*   Una vez abordados estos puntos, revisar el script `scripts/init_app.py` para entender completamente su función y asegurar que esté alineado con estas mejoras (especialmente con la ejecución de migraciones).
*   Evaluar la estructura de pruebas y añadir pruebas para las nuevas lógicas o componentes refactorizados. 