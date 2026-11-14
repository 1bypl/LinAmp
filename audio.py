"""Silnik odtwarzania oparty na QMediaPlayer (Qt Multimedia).

Qt 6 korzysta na Linuksie i Windowsie z tego samego backendu FFmpeg,
dzięki czemu obsługa formatów jest identyczna na obu systemach.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import (
    QAudioBuffer,
    QAudioBufferOutput,
    QAudioFormat,
    QAudioOutput,
    QMediaPlayer,
    QtAudio,
)

from .audioutil import AudioChunk


class AudioEngine(QObject):
    """Owija QMediaPlayer i dokłada: głośność, wyciszenie i próbki do widma."""

    positionChanged = Signal(int)      # ms
    durationChanged = Signal(int)      # ms
    playingChanged = Signal(bool)
    finished = Signal()                # utwór się skończył
    errorOccurred = Signal(str)
    samplesReady = Signal(object)      # (np.ndarray float32 mono, sample_rate)
    rawBufferReady = Signal(object)    # AudioChunk — oryginalne próbki stereo/mono
    volumeChanged = Signal(int)
    mutedChanged = Signal(bool)
    seeked = Signal(int)               # nowa pozycja w ms (przewinięcie)
    sourceChanged = Signal()           # zmiana pliku lub strumienia

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._player = QMediaPlayer(parent=self)
        self._output = QAudioOutput(parent=self)
        self._player.setAudioOutput(self._output)

        self._volume = 80
        self._muted = False
        self._eq_active = False
        self._pending_position = 0
        self._has_pending = False
        self._source_path = ""
        self._is_stream = False

        # Podsłuch zdekodowanego dźwięku — potrzebny do analizatora widma.
        self._buffer_output: QAudioBufferOutput | None = None
        try:
            self._buffer_output = QAudioBufferOutput(parent=self)
            self._player.setAudioBufferOutput(self._buffer_output)
            self._buffer_output.audioBufferReceived.connect(self._on_audio_buffer)
            self.spectrum_supported = True
        except Exception:
            self._buffer_output = None
            self.spectrum_supported = False

        self._player.positionChanged.connect(
            lambda value: self.positionChanged.emit(int(value))
        )
        self._player.durationChanged.connect(self._on_duration)
        self._player.playbackStateChanged.connect(self._on_state)
        self._player.mediaStatusChanged.connect(self._on_status)
        self._player.errorOccurred.connect(self._on_error)

        self._apply_volume()

    # --- informacje o stanie ------------------------------------------------
    @property
    def source_path(self) -> str:
        return self._source_path

    def has_source(self) -> bool:
        return bool(self._source_path)

    @property
    def is_stream(self) -> bool:
        """Czy bieżące źródło to strumień internetowy (radio)?"""
        return self._is_stream

    def position(self) -> int:
        return int(self._player.position())

    def duration(self) -> int:
        return int(self._player.duration())

    def is_playing(self) -> bool:
        return self._player.playbackState() == QMediaPlayer.PlaybackState.PlayingState

    def is_muted(self) -> bool:
        return self._muted

    def volume(self) -> int:
        return self._volume

    # --- sterowanie odtwarzaniem -------------------------------------------
    def load_file(self, path: str, position_ms: int = 0) -> None:
        """Ładuje plik bez odtwarzania (przydatne przywracania stanu)."""
        self._source_path = str(path)
        self._is_stream = False
        self._pending_position = max(0, int(position_ms))
        self._has_pending = self._pending_position > 0
        self._player.setSource(QUrl.fromLocalFile(self._source_path))
        self.sourceChanged.emit()

    def play_file(self, path: str) -> None:
        """Ładuje i od razu odtwarza plik od początku."""
        self._source_path = str(path)
        self._is_stream = False
        self._pending_position = 0
        self._has_pending = False
        self._player.setSource(QUrl.fromLocalFile(self._source_path))
        self._player.play()
        self.sourceChanged.emit()

    def play_url(self, url: str) -> None:
        """Odtwarza strumień internetowy (np. stację radiową)."""
        self._source_path = str(url)
        self._is_stream = True
        self._pending_position = 0
        self._has_pending = False
        self._player.setSource(QUrl(self._source_path))
        self._player.play()
        self.sourceChanged.emit()

    def play(self) -> None:
        if self._source_path:
            self._player.play()

    def pause(self) -> None:
        self._player.pause()

    def toggle(self) -> None:
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def stop(self) -> None:
        self._player.stop()

    def seek(self, ms: int) -> None:
        if self._source_path and self._player.isSeekable():
            target = max(0, int(ms))
            self._player.setPosition(target)
            self.seeked.emit(target)

    # --- korektor ------------------------------------------------------------
    def set_eq_active(self, active: bool) -> None:
        """Gdy korektor jest włączony, zwykłe wyjście Qt gra ciszę.

        Dźwięk jest wtedy odtwarzany przez QAudioSink w module equalizera.
        """
        active = bool(active)
        if active == self._eq_active:
            return
        self._eq_active = active
        self._apply_volume()

    # --- głośność ------------------------------------------------------------
    def set_volume(self, percent: int) -> None:
        percent = max(0, min(100, int(percent)))
        if percent == self._volume:
            return
        self._volume = percent
        self._apply_volume()
        self.volumeChanged.emit(percent)

    def set_muted(self, muted: bool) -> None:
        muted = bool(muted)
        if muted == self._muted:
            return
        self._muted = muted
        self._apply_volume()
        self.mutedChanged.emit(muted)

    @staticmethod
    def _to_linear(percent: int) -> float:
        """Zamienia pozycję suwaka (skala percepcyjna) na amplitudę."""
        value = max(0.0, min(100.0, float(percent))) / 100.0
        try:
            return float(
                QtAudio.convertVolume(
                    value,
                    QtAudio.VolumeScale.LogarithmicVolumeScale,
                    QtAudio.VolumeScale.LinearVolumeScale,
                )
            )
        except Exception:
            return value**2

    def _apply_volume(self) -> None:
        # Przy aktywnym korektorze dźwięk idzie osobnym torem (QAudioSink),
        # więc standardowe wyjście musi być wyciszone, żeby nie było echa.
        if self._eq_active or self._muted:
            target = 0.0
        else:
            target = self._to_linear(self._volume)
        self._output.setVolume(target)

    # --- wewnętrzne reakcje na sygnały Qt -----------------------------------
    def _on_state(self, state) -> None:
        self.playingChanged.emit(state == QMediaPlayer.PlaybackState.PlayingState)

    def _on_duration(self, duration_ms: int) -> None:
        self.durationChanged.emit(int(duration_ms))
        self._apply_pending_position()

    def _on_status(self, status) -> None:
        if status in (
            QMediaPlayer.MediaStatus.LoadedMedia,
            QMediaPlayer.MediaStatus.BufferedMedia,
        ):
            self._apply_pending_position()
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.finished.emit()

    def _on_error(self, error, message: str) -> None:
        if error != QMediaPlayer.Error.NoError:
            self.errorOccurred.emit(message or "Nieznany błąd odtwarzania")

    def _apply_pending_position(self) -> None:
        if not self._has_pending:
            return
        if self._player.isSeekable():
            self._player.setPosition(self._pending_position)
            self._has_pending = False

    def _on_audio_buffer(self, buffer: QAudioBuffer) -> None:
        """Zamienia bufor audio na mono float32 i wysyła do wizualizacji."""
        try:
            fmt = buffer.format()
            if not fmt.isValid():
                return
            raw = buffer.constData()
            if raw is None:
                return
            raw = bytes(raw)
            if not raw:
                return

            sample_format = fmt.sampleFormat()
            channels = max(1, fmt.channelCount())
            sample_rate = int(fmt.sampleRate()) or 48000

            if sample_format == QAudioFormat.SampleFormat.Int16:
                samples = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
                format_name = "int16"
            elif sample_format == QAudioFormat.SampleFormat.Int32:
                samples = np.frombuffer(raw, dtype="<i4").astype(np.float32) / 2147483648.0
                format_name = "int32"
            elif sample_format == QAudioFormat.SampleFormat.Float:
                samples = np.frombuffer(raw, dtype="<f4").astype(np.float32)
                format_name = "float"
            elif sample_format == QAudioFormat.SampleFormat.Double:
                samples = np.frombuffer(raw, dtype="<f8").astype(np.float32)
                format_name = "double"
            elif sample_format == QAudioFormat.SampleFormat.UInt8:
                samples = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
                format_name = "uint8"
            else:
                return

            # Oryginalny bufor (z kanałami) jest potrzebny korektorowi
            # i nagrywaniu — wysyłamy go, zanim uśrednimy próbki do mono.
            self.rawBufferReady.emit(
                AudioChunk(
                    data=raw,
                    sample_rate=sample_rate,
                    channels=channels,
                    sample_format=format_name,
                )
            )

            # Bufor jest przeplatany (kanały na przemian) — uśredniamy do mono.
            if channels > 1 and samples.size >= channels:
                usable = (samples.size // channels) * channels
                samples = samples[:usable].reshape(-1, channels).mean(axis=1)

            if samples.size:
                self.samplesReady.emit((samples, sample_rate))
        except Exception:
            # Wizualizacja nigdy nie powinna przewrócić odtwarzania.
            pass
