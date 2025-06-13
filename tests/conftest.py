"""
Configuración global de pytest
"""

import sys
import os
import pytest
from pathlib import Path

# Agregar directorio raíz al path de Python
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

# Registrar marcadores personalizados
def pytest_configure(config):
    """Registrar marcadores personalizados de pytest"""
    config.addinivalue_line(
        "markers",
        "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as a slow running test"
    )

@pytest.fixture(autouse=True)
def setup_test_env():
    """Configurar ambiente de pruebas"""
    # Crear directorios necesarios
    test_dirs = [
        root_dir / "tests" / "data",
        root_dir / "tests" / "data" / "music",
        root_dir / "tests" / "data" / "temp"
    ]
    for dir_path in test_dirs:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Limpiar directorios temporales después de las pruebas
    temp_dir = root_dir / "tests" / "data" / "temp"
    if temp_dir.exists():
        for item in temp_dir.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                item.rmdir()


# Implements Dart AI Task: Centralize Qt fixtures

@pytest.fixture(scope="session")
def qapp():
    """Provide QApplication instance for Qt tests"""
    pytest.importorskip("PyQt6")
    from PyQt6.QtWidgets import QApplication

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def qtbot(qapp):
    """Simple QtBot replacement used in tests"""
    from PyQt6.QtTest import QTest

    class QtBot:
        def addWidget(self, widget):
            widget.show()

        def wait(self, ms):
            QTest.qWait(ms)

    return QtBot()
