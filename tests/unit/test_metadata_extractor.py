"""Tests for the MetadataExtractor service."""

import os
from pathlib import Path
import pytest

pytest.importorskip("mutagen")
pytest.importorskip("scipy")
pytest.importorskip("numpy")

from scipy.io import wavfile
import numpy
from mutagen.id3 import ID3, TIT2, TPE1

from src.services.metadata_extractor import MetadataExtractor


def test_extract_id3_metadata(tmp_path):
    wav_path = tmp_path / "temp.wav"
    mp3_path = tmp_path / "temp.mp3"

    sample_rate = 44100
    duration = 1.0
    t = numpy.linspace(0, duration, int(sample_rate * duration))
    data = numpy.sin(2 * numpy.pi * 440 * t)
    data = numpy.int16(data * 32767)
    wavfile.write(wav_path, sample_rate, data)

    os.system(f'ffmpeg -i "{wav_path}" -codec:a libmp3lame -qscale:a 2 "{mp3_path}" -y -hide_banner -loglevel panic')
    wav_path.unlink()

    audio = ID3()
    audio.save(mp3_path)
    audio = ID3(mp3_path)
    audio.add(TIT2(encoding=3, text="Test Title"))
    audio.add(TPE1(encoding=3, text="Test Artist"))
    audio.save()

    extractor = MetadataExtractor()
    song = extractor.extract(mp3_path)

    assert song is not None
    assert song.title == "Test Title"
    assert song.artist == "Test Artist"
    assert song.file_path == mp3_path
