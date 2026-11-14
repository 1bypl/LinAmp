"""Zapis i odczyt ustawień oraz stanu aplikacji.

Stan trzymamy w czytelnym pliku JSON:
  Linux:   ~/.config/LinAmp/state.json
  Windows: %APPDATA%\\LinAmp\\state.json
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from . import APP_NAME


def config_dir() -> Path:
    """Zwraca (i w razie potrzeby tworzy) katalog konfiguracji aplikacji."""
    if os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    directory = base / APP_NAME

    # Migracja ze starej nazwy PyAmp — użytkownik nie traci ustawień ani playlisty.
    legacy = base / "PyAmp"
    if not directory.exists() and legacy.exists():
        try:
            legacy.rename(directory)
        except OSError:
            pass

    directory.mkdir(parents=True, exist_ok=True)
    return directory


DEFAULTS: dict[str, Any] = {
    "volume": 80,
    "muted": False,
    "shuffle": False,
    "repeat": 0,              # 0 = wyłączone, 1 = cała playlista, 2 = jeden utwór
    "geometry": None,         # zapisany rozmiar/pozycja okna (base64)
    "splitter": None,         # zapisany podział okna (base64)
    "playlist": [],           # lista ścieżek do plików
    "current": -1,            # indeks ostatnio wybranego utworu
    "position": 0,            # pozycja odtwarzania w ms
    "close_to_tray": False,   # czy zamykanie okna ma chować do zasobnika
    "playlist_visible": True,
    "radio_favorites": [],    # ulubione stacje radiowe (lista słowników)
    "language": "pl",         # pl, en, de, fr, es, ru
    "eq_enabled": False,      # korektor graficzny
    "eq_gains": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "eq_preamp": 0,
    "recordings_dir": "",     # pusty = folder Muzyka/LinAmp/Nagrania radiowe
    "recording_format": "mp3",  # mp3 (jeśli FFmpeg dostępny) albo wav
}


class Config:
    """Prosty magazyn ustawień oparty na pliku JSON."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path or (config_dir() / "state.json")
        self.data: dict[str, Any] = dict(DEFAULTS)
        self.load()

    def load(self) -> None:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                self.data.update(raw)
        except (OSError, ValueError):
            # Brak pliku lub uszkodzony JSON — po prostu używamy domyślnych.
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, DEFAULTS.get(key, default))

    def set(self, key: str, value: Any) -> None:
        self.data[key] = value

    def save(self) -> None:
        """Zapis atomowy — nie uszkodzi ustawień, jeśli zabraknie prądu."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".json.tmp")
            tmp.write_text(
                json.dumps(self.data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            os.replace(tmp, self.path)
        except OSError:
            pass
