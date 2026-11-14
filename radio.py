"""Radio internetowe — darmowy katalog stacji SHOUTcast.

Korzystamy z publicznych adresów używanych przez stronę
https://directory.shoutcast.com/ — nie potrzeba żadnego klucza API.

Wszystkie zapytania do internetu wykonujemy w tle (QRunnable), dzięki
czemu okno programu nigdy się nie zacina, nawet przy wolnym łączu.
"""

from __future__ import annotations

import html
import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, fields

from PySide6.QtCore import QObject, QRunnable, Signal

from .i18n import tr

BASE_URL = "https://directory.shoutcast.com"
TIMEOUT = 15  # sekund — po tym czasie pokazujemy czytelny komunikat

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) LinAmp/1.1"
    ),
    "Accept": "application/json, text/javascript, text/html, */*; q=0.01",
    "Accept-Language": "pl,en;q=0.8",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://directory.shoutcast.com/",
}

FAVORITES_KEY = "__favorites__"


# ---------------------------------------------------------------------------
# Model danych
# ---------------------------------------------------------------------------
@dataclass
class RadioStation:
    """Pojedyncza stacja radiowa."""

    id: str
    name: str
    genre: str = ""
    bitrate: int = 0
    format: str = ""
    listeners: int = 0
    current_track: str = ""
    website: str = ""
    stream_url: str = ""

    # --- tworzenie z danych API / zapisu ustawień --------------------------
    @classmethod
    def from_api(cls, raw: dict) -> "RadioStation":
        """Zamienia słownik zwrócony przez SHOUTcast na obiekt stacji."""
        return cls(
            id=str(raw.get("ID", "")),
            name=str(raw.get("Name", "") or tr("Nieznana stacja")).strip(),
            genre=str(raw.get("Genre", "") or "").strip(),
            bitrate=_as_int(raw.get("Bitrate")),
            format=str(raw.get("Format", "") or "").strip(),
            listeners=_as_int(raw.get("Listeners")),
            current_track=str(raw.get("CurrentTrack", "") or "").strip(),
            website=str(raw.get("IceUrl", "") or "").strip(),
        )

    @classmethod
    def from_dict(cls, raw: dict) -> "RadioStation":
        """Odtwarza stację z pliku ustawień (ulubione)."""
        known = {field.name for field in fields(cls)}
        data = {key: value for key, value in raw.items() if key in known}
        data["id"] = str(data.get("id", ""))
        data["name"] = str(data.get("name", "") or tr("Nieznana stacja"))
        data["genre"] = str(data.get("genre", "") or "")
        data["format"] = str(data.get("format", "") or "")
        data["current_track"] = str(data.get("current_track", "") or "")
        data["website"] = str(data.get("website", "") or "")
        data["bitrate"] = _as_int(data.get("bitrate"))
        data["listeners"] = _as_int(data.get("listeners"))
        return cls(**data)

    def to_dict(self) -> dict:
        """Wersja do zapisania w ustawieniach (bez adresu strumienia)."""
        data = asdict(self)
        data.pop("stream_url", None)
        return data

    # --- informacje prezentowane w tabeli ----------------------------------
    @property
    def codec(self) -> str:
        value = self.format.lower()
        if "aac" in value:
            return "AAC"
        if "ogg" in value or "opus" in value:
            return "OGG"
        if "mpeg" in value or "mp3" in value:
            return "MP3"
        return self.format.replace("audio/", "").upper() or "—"

    @property
    def quality(self) -> str:
        if self.bitrate > 0:
            return f"{self.bitrate} kbps {self.codec}"
        return self.codec


def _as_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Zapytania HTTP
# ---------------------------------------------------------------------------
def _request(url: str, data: dict | None = None) -> str:
    """Wysyła zapytanie GET/POST i zwraca odpowiedź jako tekst."""
    payload = None
    if data is not None:
        payload = urllib.parse.urlencode(data).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
        raw = response.read()
    return raw.decode("utf-8", errors="replace")


def friendly_error(error: Exception) -> str:
    """Zamienia wyjątek techniczny na komunikat zrozumiały dla użytkownika."""
    if isinstance(error, urllib.error.HTTPError):
        return tr("Serwer radia zwrócił błąd {code}. Spróbuj ponownie później.", code=error.code)
    if isinstance(error, urllib.error.URLError):
        reason = getattr(error, "reason", "")
        if isinstance(reason, TimeoutError) or "timed out" in str(reason).lower():
            return tr("Serwer radia nie odpowiada (przekroczono czas oczekiwania).")
        return tr("Brak połączenia z internetem lub serwer radia jest niedostępny.")
    if isinstance(error, TimeoutError):
        return tr("Serwer radia nie odpowiada (przekroczono czas oczekiwania).")
    if isinstance(error, ValueError):
        return tr("Serwer radia zwrócił nieoczekiwane dane.")
    return str(error) or tr("Nieznany błąd połączenia.")


def fetch_genres() -> list[str]:
    """Pobiera listę kategorii (gatunków) ze strony głównej SHOUTcast."""
    page = _request(BASE_URL + "/")
    import re

    found: dict[str, str] = {}
    for raw in re.findall(r"/Genre\?name=([^\"'&<>]+)", page):
        name = urllib.parse.unquote(html.unescape(raw)).strip()
        if name:
            found.setdefault(name.casefold(), name)
    return sorted(found.values(), key=str.casefold)


def fetch_stations(genre: str) -> list[RadioStation]:
    """Pobiera stacje należące do wybranej kategorii (maksymalnie 200)."""
    text = _request(
        BASE_URL + "/Home/BrowseByGenre",
        {"genrename": genre},
    )
    data = json.loads(text)
    if not isinstance(data, list):
        return []

    stations = []
    for item in data:
        if not isinstance(item, dict):
            continue
        station = RadioStation.from_api(item)
        if station.id and station.name:
            stations.append(station)
    return stations


def _parse_playlist(text: str) -> str:
    """Wyciąga pierwszy adres strumienia z pliku .pls albo .m3u."""
    for raw_line in text.splitlines():
        line = raw_line.strip().strip('"').strip("'")
        if not line or line.startswith("#"):
            continue
        lowered = line.lower()
        if lowered.startswith("file") and "=" in line:
            line = line.split("=", 1)[1].strip().strip('"').strip("'")
        if line.lower().startswith(("http://", "https://")):
            return line
    return ""


def _unwrap_stream_url(value: str) -> str:
    """Jeśli serwer zwrócił playlistę .pls/.m3u, wybieramy z niej strumień."""
    url = value.strip().strip('"')
    if not url.lower().startswith(("http://", "https://")):
        return ""
    if url.lower().split("?", 1)[0].endswith((".pls", ".m3u", ".m3u8")):
        try:
            playlist = _request(url)
            direct = _parse_playlist(playlist)
            if direct:
                return direct
        except Exception:
            # Zostawiamy oryginalny adres — odtwarzacz może go jeszcze obsłużyć.
            pass
    return url


def resolve_stream(station_id: str) -> str:
    """Pyta SHOUTcast o aktualny adres strumienia wybranej stacji."""
    text = _request(
        BASE_URL + "/Player/GetStreamUrl",
        {"station": str(station_id)},
    )
    try:
        data = json.loads(text)
    except ValueError:
        data = text.strip().strip('"')

    if isinstance(data, dict):
        data = data.get("StreamUrl") or data.get("streamUrl") or ""
    if not isinstance(data, str):
        return ""
    return _unwrap_stream_url(data)


def fetch_current_track(station_id: str) -> str:
    """Pobiera tytuł aktualnie granej piosenki (może być pusty)."""
    text = _request(
        BASE_URL + "/Player/GetCurrentTrack",
        {"station": str(station_id)},
    )
    try:
        data = json.loads(text)
    except ValueError:
        data = text.strip().strip('"')
    if isinstance(data, str):
        return data.strip()
    return ""


# ---------------------------------------------------------------------------
# Zadania w tle
# ---------------------------------------------------------------------------
def _safe_emit(signal, *args) -> None:
    """Emituje sygnał, ignorując sytuację, gdy aplikacja już się zamyka."""
    try:
        signal.emit(*args)
    except RuntimeError:
        pass


class RadioSignals(QObject):
    """Sygnały wspólne dla wszystkich zadań radia."""

    genresReady = Signal(list)          # list[str]
    genresFailed = Signal(str)

    stationsReady = Signal(str, list)   # gatunek, list[RadioStation]
    stationsFailed = Signal(str, str)   # gatunek, komunikat

    streamReady = Signal(str, str)      # id stacji, adres strumienia
    streamFailed = Signal(str, str)     # id stacji, komunikat

    trackReady = Signal(str, str)       # id stacji, tytuł ("" = brak danych)


class GenresTask(QRunnable):
    """Pobiera listę kategorii w tle."""

    def __init__(self, signals: RadioSignals) -> None:
        super().__init__()
        self._signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            _safe_emit(self._signals.genresReady, fetch_genres())
        except Exception as error:  # noqa: BLE001
            _safe_emit(self._signals.genresFailed, friendly_error(error))


class StationsTask(QRunnable):
    """Pobiera listę stacji dla wybranej kategorii w tle."""

    def __init__(self, genre: str, signals: RadioSignals) -> None:
        super().__init__()
        self._genre = genre
        self._signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            _safe_emit(
                self._signals.stationsReady,
                self._genre,
                fetch_stations(self._genre),
            )
        except Exception as error:  # noqa: BLE001
            _safe_emit(
                self._signals.stationsFailed,
                self._genre,
                friendly_error(error),
            )


class StreamTask(QRunnable):
    """Ustala adres strumienia wybranej stacji w tle."""

    def __init__(self, station_id: str, signals: RadioSignals) -> None:
        super().__init__()
        self._station_id = str(station_id)
        self._signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            url = resolve_stream(self._station_id)
            if not url:
                _safe_emit(
                    self._signals.streamFailed,
                    self._station_id,
                    tr("Nie udało się ustalić adresu strumienia tej stacji."),
                )
                return
            _safe_emit(self._signals.streamReady, self._station_id, url)
        except Exception as error:  # noqa: BLE001
            _safe_emit(
                self._signals.streamFailed,
                self._station_id,
                friendly_error(error),
            )


class TrackTask(QRunnable):
    """Odświeża tytuł aktualnie granej piosenki w tle."""

    def __init__(self, station_id: str, signals: RadioSignals) -> None:
        super().__init__()
        self._station_id = str(station_id)
        self._signals = signals
        self.setAutoDelete(True)

    def run(self) -> None:
        try:
            title = fetch_current_track(self._station_id)
        except Exception:  # noqa: BLE001
            title = ""
        _safe_emit(self._signals.trackReady, self._station_id, title)
