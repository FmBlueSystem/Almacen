"""Tests for MetadataExtractor with M4A files."""

import os
from pathlib import Path
import pytest

pytest.importorskip("mutagen")
pytest.importorskip("scipy")
pytest.importorskip("numpy")

from scipy.io import wavfile
import numpy
from mutagen.mp4 import MP4

from src.services.metadata_extractor import MetadataExtractor


def test_extract_m4a_bpm(tmp_path):
    wav_path = tmp_path / "temp.wav"
    m4a_path = tmp_path / "temp.m4a"

    sample_rate = 44100
    duration = 1.0
    t = numpy.linspace(0, duration, int(sample_rate * duration))
    data = numpy.sin(2 * numpy.pi * 440 * t)
    data = numpy.int16(data * 32767)
    wavfile.write(wav_path, sample_rate, data)

    os.system(
        f'ffmpeg -i "{wav_path}" -codec:a aac -b:a 192k "{m4a_path}" -y -hide_banner -loglevel panic'
    )
    wav_path.unlink()

    audio = MP4(m4a_path)
    audio["\xa9nam"] = ["M4A Title"]
    audio["\xa9ART"] = ["M4A Artist"]
    audio["tmpo"] = [130]
    audio.save()

    extractor = MetadataExtractor()
    song = extractor.extract(m4a_path)

    assert song is not None
    assert song.title == "M4A Title"
    assert song.artist == "M4A Artist"
    assert song.bpm == 130
    assert song.file_path == m4a_path
