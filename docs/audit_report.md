# Informe de Auditoría Técnica

Este documento resume los hallazgos al revisar el código del proyecto **Almacena**. Se clasifican según su impacto en la mantenibilidad y el rendimiento.

## ❗ Problemas de Alto Impacto

- **Dependencias faltantes en los tests**: La ejecución de `pytest` falla porque no se encuentran `PyQt6`, `mutagen` y `dotenv`.
  - **Evidencia**: `ModuleNotFoundError` al ejecutar `pytest -q`.
  - **Recomendación**: documentar e instalar las dependencias necesarias o crear mocks para que las pruebas puedan ejecutarse en CI.
- **Configuración duplicada en `UIConfig`** (`src/ui/config.py`): se cargan las variables de entorno directamente con `os.getenv`, en lugar de reutilizar el módulo `config` centralizado.
  - **Evidencia**: líneas 8‑24 muestran `load_dotenv()` y llamadas repetidas a `os.getenv`.
  - **Recomendación**: refactorizar para que `UIConfig` obtenga su configuración de `src/utils/config.Config`.
- **Métodos extensos en `MainWindow`** (`src/ui/windows/main_window.py`): `load_songs_for_library_view` gestiona lógica de filtrado, llamadas de servicio y actualización de UI en un mismo bloque de más de 40 líneas.
  - **Evidencia**: líneas 376‑412 del archivo.
  - **Recomendación**: dividir en métodos más pequeños (carga de datos, actualización de la vista, manejo de errores) para cumplir el principio de responsabilidad única.

## ⚠️ Problemas de Impacto Medio

- **Fixtures duplicadas** en `tests/unit/test_recursion_prevention.py` y `tests/integration/test_recursion_integration.py` para `qapp` y `qtbot`.
  - **Evidencia**: ambos archivos definen las mismas fixtures alrededor de las líneas 285 y 228 respectivamente.
  - **Recomendación**: moverlas a `tests/conftest.py` y reutilizarlas.
- **Archivos sin salto de línea final** (por ejemplo `src/utils/error_handler.py` y `src/models/base.py`).
  - **Evidencia**: al ver el final del archivo no se observa línea en blanco.
  - **Recomendación**: agregar salto de línea final conforme a PEP8.
- **Convenciones de nombres mixtas**: se mezclan identificadores en inglés y español a lo largo del código.
  - **Recomendación**: unificar el idioma de las variables y funciones para mejorar la claridad y la consistencia.

## 🔹 Mejoras de Bajo Impacto

- **Fixtures simplificables**: se implementan versiones manuales de `QtBot`; podría emplearse directamente `pytest-qt`.
- **Scripts no referenciados** (`scripts/test_config.py`, `scripts/clear_db.py`): no hay relación clara con tareas definidas.
- **Archivo `src/ui/styles/theme.py` muy extenso** (más de 500 líneas) con cadenas de QSS largas.
  - **Recomendación**: considerar fraccionar la generación de estilos en funciones auxiliares.

---

### Resultado de Pruebas

La ejecución de `pytest -q` produce múltiples errores por dependencias ausentes.

```
E   ModuleNotFoundError: No module named 'dotenv'
E   ModuleNotFoundError: No module named 'PyQt6'
E   ModuleNotFoundError: No module named 'mutagen'
```

Codex couldn't run certain commands due to environment limitations. Consider configuring a setup script or internet access in your Codex environment to install dependencies.

