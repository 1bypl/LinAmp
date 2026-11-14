"""Wspólne narzędzia do przetwarzania próbek audio.

Silnik odtwarzania przekazuje surowe bufory PCM do analizatora widma,
korektora i nagrywania. Tutaj zamieniamy je na wygodne tablice numpy
i z powrotem na 16-bitowe PCM (format używany przez pliki WAV i QAudioSink).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

_DTYPES = {
    "int16": "<i2",
    "int32": "<i4",
    "float": "<f4",
    "double": "<f8",
    "uint8": "u1",
}

_SCALES = {
    "int16": 32768.0,
    "int32": 2147483648.0,
    "float": 1.0,
    "double": 1.0,
    "uint8": 128.0,
}


@dataclass
class AudioChunk:
    """Surowe próbki z QMediaPlayer wraz z informacją o formacie."""

    data: bytes
    sample_rate: int
    channels: int
    sample_format: str


def chunk_to_float(chunk: AudioChunk) -> np.ndarray | None:
    """Zamienia bufor PCM na tablicę float32 o kształcie (ramki, kanały)."""
    dtype = _DTYPES.get(chunk.sample_format)
    if dtype is None or not chunk.data:
        return None
    try:
        raw = np.frombuffer(chunk.data, dtype=dtype)
    except (TypeError, ValueError):
        return None
    if raw.size == 0:
        return None

    channels = max(1, int(chunk.channels))
    usable = (raw.size // channels) * channels
    if usable <= 0:
        return None
    samples = raw[:usable].astype(np.float32)

    if chunk.sample_format == "uint8":
        samples = (samples - 128.0) / 128.0
    else:
        samples /= _SCALES[chunk.sample_format]

    return samples.reshape(-1, channels)


def float_to_pcm16(samples: np.ndarray) -> bytes:
    """Zamienia próbki float32 (ramki, kanały) na przeplatane PCM 16-bit."""
    if samples is None or samples.size == 0:
        return b""
    data = np.asarray(samples, dtype=np.float32)
    if data.ndim == 1:
        data = data.reshape(-1, 1)
    data = np.clip(data, -1.0, 1.0)
    pcm = (data * 32767.0).astype("<i2")
    return pcm.tobytes()


def downmix_to_stereo(samples: np.ndarray) -> np.ndarray:
    """Sprowadza dowolną liczbę kanałów do mono lub stereo."""
    if samples.ndim == 1:
        return samples.reshape(-1, 1)
    channels = samples.shape[1]
    if channels <= 2:
        return samples
    # Kanały parzyste traktujemy jako lewe, nieparzyste jako prawe.
    left = samples[:, 0::2].mean(axis=1)
    right = samples[:, 1::2].mean(axis=1)
    return np.stack((left, right), axis=1)
