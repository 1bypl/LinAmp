"""Odczyt informacji o plikach audio (tytuł, wykonawca, album, czas, okładka).

Używamy biblioteki mutagen, która obsługuje większość popularnych formatów.
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from pathlib import Path

import mutagen

# Rozszerzenia, które Qt (FFmpeg) potrafi odtworzyć na Linuksie i Windowsie.
AUDIO_EXTENSIONS = {
    ".mp3", ".flac", ".ogg", ".oga", ".opus", ".wav", ".m4a", ".aac",
    ".wma", ".aiff", ".aif", ".alac", ".wv", ".ape", ".mpc",
}

# Katalogi, których nie warto przeszukiwać przy dodawaniu folderu.
_SKIP_DIRS = {
    ".git", ".svn", "__pycache__", "$recycle.bin",
    "system volume information", "lost+found",
}


@dataclass
class TrackInfo:
    """Metadane pojedynczego utworu."""

    path: str
    title: str
    artist: str = ""
    album: str = ""
    duration_ms: int = 0
    sample_rate: int = 0
    bitrate: int = 0
    cover: bytes | None = None
    cover_mime: str = "image/jpeg"


def is_audio_file(path: str | Path) -> bool:
    return Path(path).suffix.lower() in AUDIO_EXTENSIONS


def natural_key(text: str) -> list[tuple[int, int | str]]:
    """Klucz sortowania, który rozumie liczby (utwór 2 przed utworem 10).

    Każdy element ma ten sam typ porównywania: najpierw informację, czy to
    liczba, a potem wartość. Dzięki temu nazwy zaczynające się od cyfry i od
    litery można bezpiecznie sortować w jednej liście.
    """
    parts: list[tuple[int, int | str]] = []
    digits = ""
    for char in text.lower():
        # isdecimal(), a nie isdigit(): gwarantuje, że int() przyjmie znak
        # (np. indeks górny „²” nie jest liczbą dziesiętną).
        if char.isdecimal():
            digits += char
        else:
            if digits:
                parts.append((0, int(digits)))
                digits = ""
            parts.append((1, char))
    if digits:
        parts.append((0, int(digits)))
    return parts


def scan_folder(folder: str | Path) -> list[str]:
    """Rekurencyjnie zbiera pliki audio z folderu, w naturalnej kolejności."""
    found: list[str] = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = sorted(
            (d for d in dirs if d.lower() not in _SKIP_DIRS and not d.startswith(".")),
            key=str.lower,
        )
        for name in files:
            if is_audio_file(name):
                found.append(os.path.join(root, name))
    found.sort(key=natural_key)
    return found


def _first_tag(tags, key: str) -> str:
    """Zwraca pierwszy niepusty tag jako tekst (mutagen zwraca listy)."""
    try:
        value = tags.get(key)
    except Exception:
        return ""
    if isinstance(value, (list, tuple)):
        value = value[0] if value else ""
    if value is None:
        return ""
    return str(value).strip()


def read_track(path: str | Path) -> TrackInfo:
    """Czyta metadane pliku. W razie problemów zwraca sensowne wartości domyślne."""
    path = str(path)
    stem = Path(path).stem
    info = TrackInfo(path=path, title=stem)

    audio = None
    try:
        audio = mutagen.File(path, easy=True)
    except Exception:
        audio = None

    if audio is None:
        return info

    meta = getattr(audio, "info", None)
    if meta is not None:
        try:
            info.duration_ms = int(round(float(getattr(meta, "length", 0.0)) * 1000))
        except (TypeError, ValueError):
            info.duration_ms = 0
        info.sample_rate = int(getattr(meta, "sample_rate", 0) or 0)
        info.bitrate = int(getattr(meta, "bitrate", 0) or 0)

    tags = audio.tags or {}
    info.title = _first_tag(tags, "title") or stem
    info.artist = _first_tag(tags, "artist") or _first_tag(tags, "albumartist")
    info.album = _first_tag(tags, "album")
    return info


def _sniff_mime(data: bytes) -> str:
    if data.startswith(b"\x89PNG"):
        return "image/png"
    if data.startswith(b"GIF8"):
        return "image/gif"
    if data.startswith(b"RIFF") and data[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def read_cover(path: str | Path) -> tuple[bytes | None, str]:
    """Wyciąga okładkę albumu (jeśli jest) z pliku audio."""
    try:
        audio = mutagen.File(str(path))
    except Exception:
        return None, "image/jpeg"
    if audio is None:
        return None, "image/jpeg"

    tags = getattr(audio, "tags", None)

    # MP3 / inne formaty z ramkami ID3 (APIC)
    if tags is not None:
        try:
            apic = tags.getall("APIC")
        except (AttributeError, KeyError):
            apic = None
        if apic:
            frame = apic[0]
            return bytes(frame.data), getattr(frame, "mime", "image/jpeg") or "image/jpeg"

        # MP4 / M4A (covr)
        try:
            covr = tags.get("covr")
        except Exception:
            covr = None
        if covr:
            data = bytes(covr[0])
            return data, _sniff_mime(data)

        # OGG / Opus (obrazek zakodowany w base64)
        try:
            pictures = tags.get("metadata_block_picture")
        except Exception:
            pictures = None
        if pictures:
            try:
                from mutagen.flac import Picture

                picture = Picture(base64.b64decode(pictures[0]))
                return bytes(picture.data), picture.mime or _sniff_mime(bytes(picture.data))
            except Exception:
                pass

    # FLAC — okładki trzymane osobno
    flac_pictures = getattr(audio, "pictures", None)
    if flac_pictures:
        picture = flac_pictures[0]
        return bytes(picture.data), picture.mime or _sniff_mime(bytes(picture.data))

    return None, "image/jpeg"
