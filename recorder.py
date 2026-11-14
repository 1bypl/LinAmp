"""Nagrywanie stacji radiowych do pliku WAV/MP3."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import threading
import time
import wave
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import QObject, QTimer, Signal

from .audioutil import AudioChunk, chunk_to_float, downmix_to_stereo, float_to_pcm16
from .i18n import tr


def _sanitize(name: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "_", name).strip(" .")
    return (name or "radio")[:80]


def default_recordings_dir(config) -> Path:
    custom = str(config.get("recordings_dir") or "").strip()
    if custom:
        path = Path(os.path.expanduser(custom))
    else:
        music = Path.home() / "Muzyka"
        if not music.is_dir():
            music = Path.home() / "Music"
        if not music.is_dir():
            music = Path.home()
        path = music / "LinAmp" / tr("Nagrania radiowe")
    path.mkdir(parents=True, exist_ok=True)
    return path


@dataclass
class _Encoder:
    path: str | None
    codec: str | None  # libmp3lame, aac, or None


_ENCODER: _Encoder | None = None


def _detect_encoder() -> _Encoder:
    global _ENCODER
    if _ENCODER is not None:
        return _ENCODER
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        _ENCODER = _Encoder(None, None)
        return _ENCODER
    try:
        result = subprocess.run(
            [ffmpeg, "-hide_banner", "-encoders"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        text = result.stdout + "\n" + result.stderr
    except Exception:
        text = ""
    if "libmp3lame" in text:
        codec = "libmp3lame"
    elif re.search(r"\b(?:aac|libfdk_aac)\b", text):
        codec = "aac"
    else:
        codec = None
    _ENCODER = _Encoder(ffmpeg, codec)
    return _ENCODER


class RadioRecorder(QObject):
    """Zapisuje surowe próbki z AudioEngine do WAV, a potem opcjonalnie do MP3/M4A."""

    started = Signal(str)          # ścieżka tymczasowa WAV
    finished = Signal(str, str)    # ścieżka końcowa, format (wav/mp3/m4a)
    error = Signal(str)
    elapsedChanged = Signal(int)   # sekundy

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._engine = None
        self._wav: wave.Wave_write | None = None
        self._wav_path: Path | None = None
        self._final_base: Path | None = None
        self._started_at = 0.0
        self._channels = 2
        self._sample_rate = 44100
        self._active = False
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._tick)

    @property
    def is_recording(self) -> bool:
        return self._active

    @property
    def elapsed_seconds(self) -> int:
        if not self._active:
            return 0
        return max(0, int(time.monotonic() - self._started_at))

    def start(self, station_name: str, engine, config) -> bool:
        if self._active:
            return True
        encoder = _detect_encoder()
        directory = default_recordings_dir(config)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base = directory / f"{_sanitize(station_name)} - {stamp}"
        wav_path = base.with_suffix(".wav.part")
        try:
            # Parametry ustawimy przy pierwszym buforze; otwieramy tymczasowo 2/44100.
            self._wav = wave.open(str(wav_path), "wb")
            self._wav.setnchannels(2)
            self._wav.setsampwidth(2)
            self._wav.setframerate(44100)
        except Exception as error:  # noqa: BLE001
            self._wav = None
            self.error.emit(str(error))
            return False

        self._engine = engine
        self._wav_path = wav_path
        self._final_base = base
        self._started_at = time.monotonic()
        self._channels = 0
        self._sample_rate = 0
        self._active = True
        self._timer.start()
        try:
            engine.rawBufferReady.connect(self._on_chunk)
        except Exception:
            pass
        self.started.emit(str(base))
        self.elapsedChanged.emit(0)
        return True

    def stop(self) -> None:
        if not self._active:
            return
        self._active = False
        self._timer.stop()
        if self._engine is not None:
            try:
                self._engine.rawBufferReady.disconnect(self._on_chunk)
            except Exception:
                pass
        wav_path = self._wav_path
        base = self._final_base
        try:
            if self._wav is not None:
                self._wav.close()
        except Exception:
            pass
        self._wav = None
        self._engine = None
        self._wav_path = None
        self._final_base = None

        if wav_path is None or base is None:
            return
        final_wav = base.with_suffix(".wav")
        try:
            wav_path.replace(final_wav)
        except Exception:
            final_wav = wav_path

        encoder = _detect_encoder()
        if encoder.path and encoder.codec:
            threading.Thread(
                target=self._convert,
                args=(str(final_wav), str(base), encoder.path, encoder.codec),
                daemon=True,
            ).start()
        else:
            self.finished.emit(str(final_wav), "wav")

    def _tick(self) -> None:
        self.elapsedChanged.emit(self.elapsed_seconds)

    def _on_chunk(self, chunk: AudioChunk) -> None:
        if not self._active or self._wav is None:
            return
        try:
            samples = chunk_to_float(chunk)
            if samples is None or samples.size == 0:
                return
            samples = downmix_to_stereo(samples)
            rate = int(chunk.sample_rate) or 44100
            channels = int(samples.shape[1]) if samples.ndim == 2 else 1
            if self._sample_rate == 0:
                self._sample_rate = rate
                self._channels = channels
                self._wav.setframerate(rate)
                self._wav.setnchannels(channels)
            # Jeśli format strumienia zmieni się w trakcie, zapisujemy dalej
            # w tym samym trybie (nagranie może być niespójne, ale nie gubimy).
            if rate != self._sample_rate or channels != self._channels:
                # Prosty przypadek: mono <-> stereo.
                if channels != self._channels:
                    if channels == 1 and self._channels == 2:
                        samples = samples.repeat(2, axis=1)
                    elif channels == 2 and self._channels == 1:
                        samples = samples.mean(axis=1, keepdims=True)
            pcm = float_to_pcm16(samples)
            if pcm:
                self._wav.writeframes(pcm)
        except Exception:
            # Błąd zapisu pojedynczego bufora nie może przerwać nagrywania.
            pass

    def _convert(self, wav_path: str, base: str, ffmpeg: str, codec: str) -> None:
        # Konwersja w tle — sygnały emitujemy bezpiecznie przez QTimer.singleShot? 
        # Jesteśmy w wątku tła; w Qt sygnały z innych wątków działają przy queued.
        try:
            if codec == "libmp3lame":
                out = base + ".mp3"
                cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", wav_path,
                       "-vn", "-c:a", "libmp3lame", "-b:a", "192k", out]
                fmt = "mp3"
            else:
                out = base + ".m4a"
                cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", wav_path,
                       "-vn", "-c:a", "aac", "-b:a", "160k", out]
                fmt = "m4a"
            result = subprocess.run(cmd, capture_output=True, timeout=600, check=False)
            if result.returncode == 0 and os.path.isfile(out):
                try:
                    os.remove(wav_path)
                except OSError:
                    pass
                self.finished.emit(out, fmt)
                return
        except Exception:
            pass
        self.finished.emit(wav_path, "wav")
