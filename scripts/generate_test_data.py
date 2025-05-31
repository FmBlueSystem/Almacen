#!/usr/bin/env python3
"""
Script para generar datos de prueba (archivos de audio sintéticos)
"""

import os
import sys
from pathlib import Path

# Agregar directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

import numpy as np
from scipy.io import wavfile
import mutagen
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TCON, TBPM

def create_sine_wave(frequency, duration, sample_rate=44100):
    """Crear onda sinusoidal"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    return np.sin(2 * np.pi * frequency * t)

def create_test_wav(path, frequency=440, duration=3.0):
    """Crear archivo WAV de prueba"""
    sample_rate = 44100
    data = create_sine_wave(frequency, duration, sample_rate)
    # Normalizar y convertir a int16
    data = np.int16(data * 32767)
    wavfile.write(path, sample_rate, data)

def create_test_mp3(path, metadata):
    """Crear archivo MP3 de prueba con metadatos"""
    # Primero crear WAV
    wav_path = path.with_suffix('.wav')
    create_test_wav(wav_path)
    
    # Convertir a MP3 usando ffmpeg
    os.system(f'ffmpeg -i "{wav_path}" -codec:a libmp3lame -qscale:a 2 "{path}" -y')
    
    # Eliminar WAV temporal
    wav_path.unlink()
    
    # Agregar metadatos
    audio = ID3(path)
    audio.add(TIT2(encoding=3, text=metadata['title']))
    audio.add(TPE1(encoding=3, text=metadata['artist']))
    audio.add(TALB(encoding=3, text=metadata['album']))
    audio.add(TCON(encoding=3, text=metadata['genre']))
    if 'bpm' in metadata:
        audio.add(TBPM(encoding=3, text=str(metadata['bpm'])))
    audio.save()

def main():
    """Función principal"""
    print("=== Generando datos de prueba ===")
    
    # Crear directorio de pruebas
    test_dir = root_dir / "tests" / "data" / "music"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Metadatos de ejemplo
    test_songs = [
        {
            'filename': 'song1.mp3',
            'title': 'Test Song 1',
            'artist': 'Test Artist 1',
            'album': 'Test Album 1',
            'genre': 'Rock',
            'bpm': 120
        },
        {
            'filename': 'song2.mp3',
            'title': 'Test Song 2',
            'artist': 'Test Artist 2',
            'album': 'Test Album 1',
            'genre': 'Pop',
            'bpm': 128
        },
        {
            'filename': 'song3.mp3',
            'title': 'Test Song 3',
            'artist': 'Test Artist 1',
            'album': 'Test Album 2',
            'genre': 'Jazz',
            'bpm': 90
        }
    ]
    
    try:
        for song in test_songs:
            path = test_dir / song['filename']
            print(f"Creando {path.name}...")
            create_test_mp3(path, song)
            print(f"✓ {path.name} creado con metadatos")
        
        print("\n=== Datos de prueba generados exitosamente ===")
        print(f"Ubicación: {test_dir}")
        return 0
        
    except Exception as e:
        print(f"Error generando datos de prueba: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
