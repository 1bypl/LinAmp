"""Graficzny korektor 10-pasmowy dla LinAmp.

Qt Multimedia nie ma wbudowanego korektora, dlatego dźwięk z QMediaPlayer
przechwytujemy przez QAudioBufferOutput, przetwarzamy w numpy (FFT + nakładanie
okien) i odtwarzamy przez QAudioSink. Zwykłe wyjście Qt jest wtedy wyciszone,
więc nie ma podwójnego dźwięku. Gdy korektor jest wyłączony, wszystko działa
dokładnie tak jak wcześniej — bez dodatkowego opóźnienia i bez QAudioSink.
"""

from __future__ import annotations

import numpy as np
from PySide6.QtCore import QObject, QTimer, Signal
from PySide6.QtMultimedia import (
    QAudio,
    QAudioFormat,
    QAudioSink,
    QMediaDevices,
    QtAudio,
)

from .audioutil import AudioChunk, chunk_to_float, downmix_to_stereo, float_to_pcm16
from .i18n import tr

# Częstotliwości środkowe pasm (Hz) — typowy korektor graficzny.
EQ_FREQUENCIES = (31, 62, 125, 250, 500, 1000, 2000, 4000, 8000, 16000)

# Wartości w decybelach dla poszczególnych presetów.
EQ_PRESETS: dict[str, tuple[float, ...]] = {
    "Płaski": (0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
    "Rock": (5, 4, 3, 1, -1, -1, 0, 2, 3, 4),
    "Pop": (-1, 0, 1, 3, 4, 3, 1, 0, -1, -1),
    "Bas": (7, 6, 5, 3, 1, 0, 0, 0, 0, 0),
    "Wokal": (-2, -1, 0, 1, 3, 4, 4, 2, 0, -1),
    "Klasyczny": (3, 2, 1, 0, -1, -1, 0, 1, 2, 3),
    "Elektroniczny": (5, 4, 2, 0, -1, 0, 2, 3, 4, 5),
}


class Equalizer(QObject):
    """Korektor podłączony do silnika AudioEngine."""

    failed = Signal(str)

    HOP = 1024
    FFT_SIZE = 2 * HOP

    def __init__(self, engine, parent=None) -> None:
        super().__init__(parent)
        self._engine = engine
        self._enabled = False
        self._gains = [0.0] * len(EQ_FREQUENCIES)
        self._preamp = 0.0

        self._sink: QAudioSink | None = None
        self._io = None
        self._sink_key: tuple[int, int] | None = None
        self._queue = bytearray()
        self._timer = QTimer(self)
        self._timer.setInterval(10)
        self._timer.timeout.connect(self._flush)

        # Stan filtrów (ciągłość między buforami).
        self._pending = np.zeros((0, 1), dtype=np.float32)
        self._prev_input = np.zeros((self.HOP, 1), dtype=np.float32)
        self._overlap = np.zeros((self.HOP, 1), dtype=np.float32)
        self._channels = 1
        self._sample_rate = 48000
        self._window = np.sqrt(np.hanning(self.FFT_SIZE)).astype(np.float32)
        self._response_cache: dict[tuple, np.ndarray] = {}

        self._engine.rawBufferReady.connect(self._on_chunk)
        self._engine.playingChanged.connect(self._on_playing)
        self._engine.volumeChanged.connect(lambda _value: self._apply_volume())
        self._engine.mutedChanged.connect(lambda _value: self._apply_volume())
        self._engine.seeked.connect(lambda _value: self._reset_stream())
        self._engine.sourceChanged.connect(self._reset_stream)

    # --- informacje ---------------------------------------------------------
    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def available(self) -> bool:
        try:
            return not QMediaDevices.defaultAudioOutput().isNull()
        except Exception:
            return False

    @property
    def gains(self) -> list[float]:
        return list(self._gains)

    @property
    def preamp(self) -> float:
        return self._preamp

    # --- ustawienia ---------------------------------------------------------
    def set_gains(self, gains) -> None:
        values = [float(value) for value in gains][: len(EQ_FREQUENCIES)]
        while len(values) < len(EQ_FREQUENCIES):
            values.append(0.0)
        self._gains = [max(-12.0, min(12.0, value)) for value in values]
        self._response_cache.clear()

    def set_preamp(self, value: float) -> None:
        self._preamp = max(-12.0, min(12.0, float(value)))
        self._response_cache.clear()

    def set_enabled(self, enabled: bool) -> bool:
        enabled = bool(enabled)
        if enabled == self._enabled:
            return True

        if enabled:
            if not self.available:
                self.failed.emit(tr("Korektor jest niedostępny na tym systemie."))
                return False
            self._enabled = True
            self._engine.set_eq_active(True)
            self._apply_volume()
            self._reset_stream()
            return True

        self._enabled = False
        self._engine.set_eq_active(False)
        self._stop_sink()
        self._reset_stream()
        return True

    def shutdown(self) -> None:
        if self._enabled:
            self._enabled = False
            self._engine.set_eq_active(False)
        self._timer.stop()
        self._stop_sink()

    # --- obsługa buforów ----------------------------------------------------
    def _on_chunk(self, chunk: AudioChunk) -> None:
        if not self._enabled or not self._engine.is_playing():
            return
        samples = chunk_to_float(chunk)
        if samples is None or samples.size == 0:
            return
        samples = downmix_to_stereo(samples)
        channels = int(samples.shape[1])
        rate = int(chunk.sample_rate) or 48000

        if not self._ensure_sink(rate, channels):
            return

        if self._channels != channels:
            self._reset_filters(channels)
        if self._sample_rate != rate:
            self._sample_rate = rate
            self._reset_filters(channels)

        # Łączymy nowe próbki z tym, co zostało z poprzedniego bufora.
        if self._pending.size == 0:
            self._pending = samples.copy()
        else:
            self._pending = np.concatenate((self._pending, samples), axis=0)

        while self._pending.shape[0] >= self.HOP:
            block = self._pending[: self.HOP]
            self._pending = self._pending[self.HOP :]
            processed = self._process_block(block, rate)
            self._queue.extend(float_to_pcm16(processed))

        # Nie pozwalamy kolejce rosnąć w nieskończoność (np. przy zwolnionym
        # odtwarzaniu). Zostawiamy maksymalnie ok. 2 sekundy dźwięku.
        max_queue = max(8192, rate * channels * 2 * 2)
        if len(self._queue) > max_queue:
            del self._queue[: len(self._queue) - max_queue]

        self._flush()
        if self._queue and not self._timer.isActive():
            self._timer.start()

    def _process_block(self, block: np.ndarray, rate: int) -> np.ndarray:
        channels = int(block.shape[1])
        output = np.empty_like(block, dtype=np.float32)
        response = self._response(rate)

        for channel in range(channels):
            frame = np.concatenate(
                (self._prev_input[:, channel], block[:, channel])
            ).astype(np.float32)
            spectrum = np.fft.rfft(frame * self._window) * response
            filtered = np.fft.irfft(spectrum, n=self.FFT_SIZE).astype(np.float32)
            filtered *= self._window
            output[:, channel] = filtered[: self.HOP] + self._overlap[:, channel]
            self._overlap[:, channel] = filtered[self.HOP :]
            self._prev_input[:, channel] = block[:, channel]

        return np.clip(output, -1.0, 1.0)

    def _response(self, rate: int) -> np.ndarray:
        key = (int(rate), tuple(round(g, 2) for g in self._gains), round(self._preamp, 2))
        cached = self._response_cache.get(key)
        if cached is not None:
            return cached

        freqs = np.fft.rfftfreq(self.FFT_SIZE, 1.0 / max(1, rate))
        decibels = np.full(freqs.shape, self._preamp, dtype=np.float32)
        for center, gain in zip(EQ_FREQUENCIES, self._gains):
            if abs(gain) < 0.01:
                continue
            ratio = np.maximum(freqs, 1.0) / float(center)
            # Miękka krzywa w skali oktawowej — bez ostrych rezonansów.
            bump = np.exp(-0.5 * (np.log2(ratio) / 0.75) ** 2)
            decibels += float(gain) * bump

        decibels = np.clip(decibels, -24.0, 24.0)
        response = np.power(10.0, decibels / 20.0).astype(np.float32)
        self._response_cache[key] = response
        # Cache nie musi rosnąć bez końca przy przeciąganiu suwaków.
        if len(self._response_cache) > 24:
            self._response_cache.pop(next(iter(self._response_cache)))
        return response

    # --- QAudioSink ---------------------------------------------------------
    def _ensure_sink(self, rate: int, channels: int) -> bool:
        key = (int(rate), int(channels))
        if self._sink is not None and self._sink_key == key:
            return True

        self._stop_sink()
        try:
            device = QMediaDevices.defaultAudioOutput()
            if device.isNull():
                self._fail(tr("Korektor jest niedostępny na tym systemie."))
                return False

            fmt = QAudioFormat()
            fmt.setSampleRate(int(rate))
            fmt.setChannelCount(int(channels))
            fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)

            sink = QAudioSink(device, fmt, self)
            # 200 ms zapasu chroni przed trzaskami przy chwilowym obciążeniu.
            sink.setBufferSize(max(8192, int(rate * channels * 2 * 0.20)))
            io = sink.start()
            if io is None or sink.error() != QAudio.Error.NoError:
                raise RuntimeError("QAudioSink nie uruchomił się")

            self._sink = sink
            self._io = io
            self._sink_key = key
            self._apply_volume()
            self._reset_filters(int(channels))
            self._sample_rate = int(rate)
            return True
        except Exception as error:  # noqa: BLE001
            self._fail(str(error) or "Nieznany błąd korektora")
            return False

    def _stop_sink(self) -> None:
        self._timer.stop()
        self._queue.clear()
        sink = self._sink
        self._sink = None
        self._io = None
        self._sink_key = None
        if sink is not None:
            try:
                sink.stop()
            except Exception:
                pass
            sink.deleteLater()

    def _flush(self) -> None:
        if self._sink is None or self._io is None:
            self._timer.stop()
            return
        try:
            while self._queue:
                free = int(self._sink.bytesFree())
                if free <= 0:
                    break
                part = bytes(self._queue[:free])
                written = int(self._io.write(part))
                if written < 0:
                    raise RuntimeError("Nie można zapisać dźwięku do QAudioSink")
                if written == 0:
                    break
                del self._queue[:written]
        except Exception as error:  # noqa: BLE001
            self._fail(str(error) or "Nieznany błąd korektora")
            return
        if not self._queue:
            self._timer.stop()

    # --- reakcje na silnik --------------------------------------------------
    def _on_playing(self, playing: bool) -> None:
        if not self._enabled:
            return
        if not playing:
            self._stop_sink()
            self._reset_stream()

    def _apply_volume(self) -> None:
        if self._sink is None:
            return
        if self._engine.is_muted():
            target = 0.0
        else:
            value = max(0.0, min(100.0, float(self._engine.volume()))) / 100.0
            try:
                target = float(
                    QtAudio.convertVolume(
                        value,
                        QtAudio.VolumeScale.LogarithmicVolumeScale,
                        QtAudio.VolumeScale.LinearVolumeScale,
                    )
                )
            except Exception:
                target = value**2
        self._sink.setVolume(target)

    def _reset_stream(self) -> None:
        self._pending = np.zeros((0, max(1, self._channels)), dtype=np.float32)
        self._reset_filters(self._channels)
        self._queue.clear()

    def _reset_filters(self, channels: int) -> None:
        channels = max(1, int(channels))
        self._channels = channels
        self._prev_input = np.zeros((self.HOP, channels), dtype=np.float32)
        self._overlap = np.zeros((self.HOP, channels), dtype=np.float32)

    def _fail(self, message: str) -> None:
        was_enabled = self._enabled
        self._enabled = False
        self._engine.set_eq_active(False)
        self._stop_sink()
        if was_enabled:
            self.failed.emit(message)
