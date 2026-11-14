"""Model playlisty, filtrowanie, sortowanie oraz pliki M3U/M3U8 i PLS."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PySide6.QtGui import QColor

from .i18n import tr
from .metadata import TrackInfo
from .theme import ACCENT, MUTED

# Własne role danych (Qt pozwala dokładać własne role ponad standardowe).
SORT_ROLE = Qt.ItemDataRole.UserRole + 10
PATH_ROLE = Qt.ItemDataRole.UserRole + 11
TRACK_ROLE = Qt.ItemDataRole.UserRole + 12


def _norm(path: str) -> str:
    """Klucz do porównywania ścieżek (niezależny od wielkości liter na Windowsie)."""
    return os.path.normcase(os.path.abspath(path))


def format_duration(ms: int) -> str:
    """Zamienia milisekundy na czytelny czas: 3:45 albo 1:02:03."""
    if not ms or ms < 0:
        return "--:--"
    total = int(round(ms / 1000))
    hours, rest = divmod(total, 3600)
    minutes, seconds = divmod(rest, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


@dataclass
class Track:
    """Pojedynczy utwór na playliście."""

    path: str
    title: str
    artist: str = ""
    album: str = ""
    duration_ms: int = 0

    @classmethod
    def from_path(cls, path: str) -> "Track":
        return cls(path=str(path), title=Path(path).stem)

    @classmethod
    def from_info(cls, info: TrackInfo) -> "Track":
        return cls(
            path=info.path,
            title=info.title or Path(info.path).stem,
            artist=info.artist,
            album=info.album,
            duration_ms=info.duration_ms,
        )


class PlaylistModel(QAbstractTableModel):
    """Tabela z utworami. Kolumny: #, Tytuł, Wykonawca, Album, Czas."""

    HEADERS = ("#", "Tytuł", "Wykonawca", "Album", "Czas")

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._tracks: list[Track] = []
        self._by_path: dict[str, int] = {}
        self._current_path: str | None = None

    # --- podstawowe API modelu ---------------------------------------------
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else len(self._tracks)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: B008
        return 0 if parent.isValid() else len(self.HEADERS)

    def headerData(self, section: int, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return tr(self.HEADERS[section])
        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None
        row, col = index.row(), index.column()
        track = self._tracks[row]

        if role == Qt.ItemDataRole.DisplayRole:
            return (
                str(row + 1),
                track.title,
                track.artist,
                track.album,
                format_duration(track.duration_ms),
            )[col]

        if role == SORT_ROLE:
            if col == 0:
                return row
            if col == 1:
                return track.title.lower()
            if col == 2:
                return track.artist.lower()
            if col == 3:
                return track.album.lower()
            return track.duration_ms

        if role == PATH_ROLE:
            return track.path
        if role == TRACK_ROLE:
            return track
        if role == Qt.ItemDataRole.ToolTipRole:
            return track.path

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col == 0:
                return Qt.AlignmentFlag.AlignCenter
            if col == 4:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

        # Wyróżnienie aktualnie odtwarzanego utworu.
        if track.path == self._current_path:
            if role == Qt.ItemDataRole.ForegroundRole:
                return QColor(ACCENT) if col in (1, 4) else QColor("#cfd6df")
            if role == Qt.ItemDataRole.BackgroundRole:
                return QColor(30, 215, 96, 20)
        elif role == Qt.ItemDataRole.ForegroundRole and col in (0, 4):
            return QColor(MUTED)
        return None

    # --- zarządzanie utworami ----------------------------------------------
    def tracks(self) -> list[Track]:
        return self._tracks

    def track_at(self, row: int) -> Track | None:
        if 0 <= row < len(self._tracks):
            return self._tracks[row]
        return None

    def row_of(self, path: str) -> int:
        return self._by_path.get(_norm(path), -1)

    def paths(self) -> list[str]:
        return [t.path for t in self._tracks]

    def total_duration_ms(self) -> int:
        return sum(t.duration_ms for t in self._tracks)

    def add_paths(self, paths: list[str]) -> list[str]:
        """Dodaje ścieżki (bez duplikatów). Zwraca listę faktycznie dodanych."""
        fresh: list[Track] = []
        for path in paths:
            key = _norm(path)
            if key in self._by_path:
                continue
            track = Track.from_path(path)
            self._by_path[key] = len(self._tracks) + len(fresh)
            fresh.append(track)
        if not fresh:
            return []
        start = len(self._tracks)
        self.beginInsertRows(QModelIndex(), start, start + len(fresh) - 1)
        self._tracks.extend(fresh)
        self.endInsertRows()
        return [t.path for t in fresh]

    def add_tracks(self, tracks: list[Track]) -> None:
        if not tracks:
            return
        start = len(self._tracks)
        self.beginInsertRows(QModelIndex(), start, start + len(tracks) - 1)
        for track in tracks:
            self._by_path[_norm(track.path)] = len(self._tracks)
            self._tracks.append(track)
        self.endInsertRows()

    def update_metadata(self, info: TrackInfo) -> None:
        row = self._by_path.get(_norm(info.path))
        if row is None:
            return
        track = self._tracks[row]
        track.title = info.title or Path(info.path).stem
        track.artist = info.artist
        track.album = info.album
        track.duration_ms = info.duration_ms
        self.dataChanged.emit(
            self.index(row, 0), self.index(row, len(self.HEADERS) - 1)
        )

    def update_duration(self, path: str, duration_ms: int) -> None:
        row = self._by_path.get(_norm(path))
        if row is None or duration_ms <= 0:
            return
        track = self._tracks[row]
        if track.duration_ms == duration_ms:
            return
        track.duration_ms = duration_ms
        self.dataChanged.emit(self.index(row, 4), self.index(row, 4))

    def set_current_path(self, path: str | None) -> None:
        old = self._current_path
        if old == path:
            return
        self._current_path = path
        for candidate in (old, path):
            if not candidate:
                continue
            row = self._by_path.get(_norm(candidate))
            if row is not None:
                self.dataChanged.emit(
                    self.index(row, 0), self.index(row, len(self.HEADERS) - 1)
                )

    def remove_rows(self, rows: list[int]) -> None:
        """Usuwa wskazane wiersze (grupami, żeby nie odświeżać widoku 100 razy)."""
        if not rows:
            return
        groups: list[list[int]] = []
        for row in sorted(set(rows)):
            if groups and row == groups[-1][1] + 1:
                groups[-1][1] = row
            else:
                groups.append([row, row])

        for start, end in reversed(groups):
            self.beginRemoveRows(QModelIndex(), start, end)
            del self._tracks[start : end + 1]
            self.endRemoveRows()

        self._reindex()

    def clear(self) -> None:
        self.beginResetModel()
        self._tracks.clear()
        self._by_path.clear()
        self._current_path = None
        self.endResetModel()

    def _reindex(self) -> None:
        self._by_path = {_norm(t.path): i for i, t in enumerate(self._tracks)}
        if self._current_path and _norm(self._current_path) not in self._by_path:
            self._current_path = None


class PlaylistProxy(QSortFilterProxyModel):
    """Filtrowanie po tekście i sortowanie kolumn (bez zmiany kolejności źródła)."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setDynamicSortFilter(True)
        self.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.setSortLocaleAware(True)
        self.setSortRole(SORT_ROLE)
        self._terms: list[str] = []

    def set_filter(self, text: str) -> None:
        self._terms = [term for term in text.lower().split() if term]
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        if not self._terms:
            return True
        model: PlaylistModel = self.sourceModel()  # type: ignore[assignment]
        track = model.track_at(source_row)
        if track is None:
            return False
        haystack = f"{track.title} {track.artist} {track.album} {track.path}".lower()
        return all(term in haystack for term in self._terms)


# --- pliki playlist M3U / M3U8 / PLS --------------------------------------
def _is_url(value: str) -> bool:
    return urlparse(value).scheme.lower() in ("http", "https", "rtsp", "mms", "icy")


def _resolve_path(value: str, playlist_path: Path) -> str:
    """Ścieżki względne rozwiązujemy względem pliku playlisty."""
    if _is_url(value):
        return value
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = (playlist_path.parent / candidate).resolve()
    return str(candidate)


def _split_label(label: str) -> tuple[str, str]:
    """Z etykiety „Wykonawca - Tytuł” wyciąga wykonawcę i tytuł."""
    label = label.strip()
    if " - " in label:
        artist, title = label.split(" - ", 1)
        return artist.strip(), title.strip()
    return "", label


def save_m3u(tracks: list[Track], path: str | Path) -> None:
    """Zapisuje playlistę w formacie M3U8 (UTF-8, kompatybilnym z Winampem)."""
    lines = ["#EXTM3U"]
    for track in tracks:
        seconds = int(round(track.duration_ms / 1000))
        label = f"{track.artist} - {track.title}" if track.artist else track.title
        label = label.replace("\r", " ").replace("\n", " ")
        lines.append(f"#EXTINF:{seconds},{label}")
        lines.append(track.path)
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_m3u(path: str | Path) -> list[Track]:
    """Wczytuje playlistę M3U/M3U8. Ścieżki względne rozwiązuje poprawnie."""
    playlist_path = Path(path)
    try:
        text = playlist_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = playlist_path.read_text(encoding="cp1250", errors="replace")

    tracks: list[Track] = []
    pending_title = ""
    pending_duration = 0
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("#EXTINF:"):
            info = line[8:]
            try:
                length_text, label = info.split(",", 1)
                pending_duration = max(0, int(float(length_text))) * 1000
            except ValueError:
                pending_duration = 0
                label = info.split(",", 1)[-1]
            pending_title = label.strip()
            continue
        if line.startswith("#"):
            continue

        resolved = _resolve_path(line, playlist_path)
        artist, title = _split_label(pending_title)
        track = Track.from_path(resolved)
        if title:
            track.title = title
        track.artist = artist
        track.duration_ms = pending_duration
        tracks.append(track)
        pending_title = ""
        pending_duration = 0
    return tracks


def save_pls(tracks: list[Track], path: str | Path) -> None:
    """Zapisuje playlistę w formacie PLS (obsługiwanym przez Winamp i VLC)."""
    lines = ["[playlist]", f"NumberOfEntries={len(tracks)}"]
    for index, track in enumerate(tracks, start=1):
        label = f"{track.artist} - {track.title}" if track.artist else track.title
        label = label.replace("\r", " ").replace("\n", " ")
        lines.append(f"File{index}={track.path}")
        lines.append(f"Title{index}={label}")
        lines.append(f"Length{index}={max(0, int(round(track.duration_ms / 1000)))}")
    lines.append("Version=2")
    Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")


_PLS_LINE = re.compile(r"^(File|Title|Length)(\d+)\s*=\s*(.*)$", re.IGNORECASE)


def load_pls(path: str | Path) -> list[Track]:
    """Wczytuje playlistę PLS. Obsługuje też adresy strumieni internetowych."""
    playlist_path = Path(path)
    try:
        text = playlist_path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        text = playlist_path.read_text(encoding="cp1250", errors="replace")

    entries: dict[int, dict[str, str]] = {}
    for raw_line in text.splitlines():
        match = _PLS_LINE.match(raw_line.strip())
        if not match:
            continue
        kind, number, value = match.groups()
        entries.setdefault(int(number), {})[kind.lower()] = value.strip()

    tracks: list[Track] = []
    for number in sorted(entries):
        entry = entries[number]
        file_value = entry.get("file", "")
        if not file_value:
            continue
        resolved = _resolve_path(file_value, playlist_path)
        artist, title = _split_label(entry.get("title", ""))
        track = Track.from_path(resolved)
        if title:
            track.title = title
        track.artist = artist
        try:
            track.duration_ms = max(0, int(float(entry.get("length", "0")))) * 1000
        except ValueError:
            track.duration_ms = 0
        tracks.append(track)
    return tracks


def load_playlist(path: str | Path) -> list[Track]:
    """Wczytuje playlistę na podstawie rozszerzenia (.pls albo .m3u/.m3u8)."""
    if Path(path).suffix.lower() == ".pls":
        return load_pls(path)
    return load_m3u(path)


def save_playlist(tracks: list[Track], path: str | Path) -> None:
    """Zapisuje playlistę na podstawie rozszerzenia (.pls albo .m3u/.m3u8)."""
    if Path(path).suffix.lower() == ".pls":
        save_pls(tracks, path)
    else:
        save_m3u(tracks, path)
