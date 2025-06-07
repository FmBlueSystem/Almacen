"""
Pruebas para el servicio de gestión de música
"""

import pytest

# Implements Dart AI Task: Skip tests if mutagen is missing
pytest.importorskip("mutagen")

import shutil
from pathlib import Path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.services.music_service import MusicService
from src.database.connection import DatabaseConnection
from src.models.song import Song
from src.database.migrations import MigrationManager

# Configuración de pruebas
@pytest.fixture
def test_db():
    """Crear base de datos temporal para pruebas"""
    db_path = Path("tests/data/test.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    db = DatabaseConnection(str(db_path))
    
    # Ejecutar migraciones en la base de datos de prueba
    migration_mgr = MigrationManager(db)
    migration_mgr.run_migrations()
    
    yield db
    
    # Limpiar después de las pruebas
    if db_path.exists():
        db_path.unlink()

@pytest.fixture
def test_music_dir():
    """Crear directorio temporal con archivos de música"""
    music_dir = Path("tests/data/music")
    music_dir.mkdir(parents=True, exist_ok=True)
    
    # Aquí deberías copiar archivos de música de prueba
    # Por ahora solo creamos el directorio
    
    yield music_dir
    
    # Limpiar después de las pruebas
    if music_dir.exists():
        shutil.rmtree(music_dir)

@pytest.fixture
def music_service(test_db):
    """Crear servicio de música para pruebas"""
    service = MusicService(test_db)
    return service

def test_import_folder(music_service, test_music_dir):
    """Probar importación de carpeta"""
    # Omitir esta prueba si scipy o numpy no están instalados
    scipy = pytest.importorskip("scipy")
    numpy = pytest.importorskip("numpy") # numpy también es usado aquí
    
    # Limpiar directorio de prueba
    if test_music_dir.exists():
        shutil.rmtree(test_music_dir)
    test_music_dir.mkdir(parents=True)
    
    # Generar archivos de audio directamente con SciPy y convertirlos a MP3
    # mediante ffmpeg
    # import numpy as np -> ya importado a través de pytest.importorskip
    # from scipy.io import wavfile -> scipy.io.wavfile estará disponible si la prueba no se omite
    from scipy.io import wavfile # Mantener para claridad, aunque scipy ya está importado
    pytest.importorskip("mutagen")
    import mutagen
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON
    
    # Crear archivo WAV temporal
    wav_path = test_music_dir / "test.wav"
    sample_rate = 44100
    duration = 1.0  # 1 segundo
    t = numpy.linspace(0, duration, int(sample_rate * duration))
    data = numpy.sin(2 * numpy.pi * 440 * t)  # Tono A-440Hz
    data = numpy.int16(data * 32767)
    wavfile.write(wav_path, sample_rate, data)
    
    # Convertir a MP3
    import os
    mp3_path = test_music_dir / "test.mp3"
    os.system(f'ffmpeg -i "{wav_path}" -codec:a libmp3lame -qscale:a 2 "{mp3_path}" -y -hide_banner -loglevel panic')
    wav_path.unlink()
    
    # Agregar metadatos
    audio = ID3()
    audio.save(mp3_path)  # Crear archivo ID3 vacío primero
    audio = ID3(mp3_path)
    audio.add(TIT2(encoding=3, text="Test Song"))
    audio.add(TPE1(encoding=3, text="Test Artist"))
    audio.add(TALB(encoding=3, text="Test Album"))
    audio.add(TCON(encoding=3, text="Test Genre"))
    audio.save()
    
    # Ejecutar
    imported, failed = music_service.import_folder(str(test_music_dir))
    
    # Verificar
    assert imported == 1  # Un archivo importado
    assert failed == 0  # Sin fallos

def test_search_songs(music_service):
    """Probar búsqueda de canciones"""
    # Preparar
    song = Song(
        id=None,
        title="Test Song",
        artist="Test Artist",
        album="Test Album",
        genre="Test Genre",
        bpm=120,
        file_path=Path("tests/data/music/test.mp3")
    )
    music_service.songs.add(song)
    
    # Ejecutar
    songs, total_items_found = music_service.search_songs(
        title="Test",
        artist="Artist",
        page=1,
        per_page=10
    )
    
    # Verificar
    assert len(songs) == 1
    assert songs[0].title == "Test Song"
    assert songs[0].artist == "Test Artist"
    assert total_items_found == 1

def test_pagination(music_service, test_music_dir):
    """Probar paginación de resultados"""
    # Limpiar directorio y base de datos
    if test_music_dir.exists():
        shutil.rmtree(test_music_dir)
    test_music_dir.mkdir(parents=True)
    
    # Crear canciones en orden específico
    for i in range(55):  # Crear 55 canciones
        song = Song(
            id=None,
            title=f"Song {i:03d}",  # Usar padding para asegurar orden correcto
            artist=f"Artist {i:03d}",
            album=f"Album {i:03d}",
            genre="Test Genre",
            bpm=120,
            file_path=Path(f"tests/data/music/song_{i:03d}.mp3")
        )
        music_service.songs.add(song)
    
    # Ejecutar
    songs, total_pages = music_service.get_songs(page=2, per_page=20)
    
    # Verificar
    assert len(songs) == 20  # Segunda página completa
    assert total_pages == 3  # 55 canciones / 20 por página = 3 páginas
    assert songs[0].title == "Song 020"  # Primera canción de la segunda página


def test_import_files(music_service, test_music_dir):
    """Probar importación de archivos individuales"""
    # Omitir esta prueba si scipy o numpy no están instalados
    scipy = pytest.importorskip("scipy")
    numpy = pytest.importorskip("numpy")

    from scipy.io import wavfile  # Importado solo si la prueba no se omite
    pytest.importorskip("mutagen")
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON
    import os

    # Limpiar y recrear directorio de prueba
    if test_music_dir.exists():
        shutil.rmtree(test_music_dir)
    test_music_dir.mkdir(parents=True)

    mp3_paths = []
    for i in range(2):
        wav_path = test_music_dir / f"temp{i}.wav"
        mp3_path = test_music_dir / f"temp{i}.mp3"

        sample_rate = 44100
        duration = 1.0
        t = numpy.linspace(0, duration, int(sample_rate * duration))
        data = numpy.sin(2 * numpy.pi * 440 * t)
        data = numpy.int16(data * 32767)
        wavfile.write(wav_path, sample_rate, data)

        os.system(
            f'ffmpeg -i "{wav_path}" -codec:a libmp3lame -qscale:a 2 "{mp3_path}" -y -hide_banner -loglevel panic'
        )
        wav_path.unlink()

        audio = ID3()
        audio.save(mp3_path)
        audio = ID3(mp3_path)
        audio.add(TIT2(encoding=3, text=f"Test Song {i}"))
        audio.add(TPE1(encoding=3, text="Test Artist"))
        audio.add(TALB(encoding=3, text="Test Album"))
        audio.add(TCON(encoding=3, text="Test Genre"))
        audio.save()

        mp3_paths.append(str(mp3_path))

    # Agregar un archivo inexistente a la lista
    nonexistent = str(test_music_dir / "does_not_exist.mp3")
    file_list = mp3_paths + [nonexistent]

    imported, failed = music_service.import_files(file_list)

    assert imported == 2
    assert failed == 1
    assert music_service.get_total_songs_count() == 2
