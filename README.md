# LinAmp 🎵

Nowoczesny odtwarzacz muzyczny inspirowany Winampem — z **darmowym radiem
internetowym**, korektorem, nagrywaniem stacji i obsługą wielu formatów.
Działa na **Linuksie** i **Windowsie**.

Interfejs jest dostępny w językach: **polski (domyślny), angielski, niemiecki,
francuski, hiszpański i rosyjski**.

![Okno główne LinAmp](docs/okno-glowne.png)

## Najważniejsze funkcje

- **Odtwarzanie muzyki:** MP3, FLAC, OGG/Opus, WAV, M4A/AAC, WMA i inne formaty
  obsługiwane przez FFmpeg.
- **Playlista:** filtrowanie, sortowanie, przewijanie, losowe odtwarzanie,
  powtarzanie, wczytywanie i zapis **M3U/M3U8 oraz PLS**.
- **Korektor graficzny (10 pasm):** presety (np. Rock, Pop, Bas, Wokal,
  Klasyczny, Elektroniczny) i własne ustawienia, działa dla muzyki i radia.
- **Radio internetowe SHOUTcast:** darmowy katalog (bez rejestracji i klucza
  API), kategorie, wyszukiwanie, ulubione stacje, podgląd aktualnie granej
  piosenki oraz **nagrywanie stacji**.
- **Analizator widma (FFT)** reagujący na odtwarzany dźwięk.
- **Okładki i tagi:** tytuł, wykonawca, album i czas trwania.
- **Zasobnik systemowy**, skróty klawiszowe i obsługa klawiszy multimedialnych.
- **Przeciąganie i upuszczanie** plików/folderów na okno programu.

![Okno radia](docs/radio.png)

---

## Instalacja i uruchamianie na Linuksie

### Opcja 1: AppImage (najprostsza, bez instalacji Pythona)

1. Pobierz/skopiuj plik:
   `dist/LinAmp-1.2.0-x86_64.AppImage`
2. Nadaj prawo uruchamiania (jeśli potrzeba):
   ```bash
   chmod +x LinAmp-1.2.0-x86_64.AppImage
   ```
3. Uruchom:
   ```bash
   ./LinAmp-1.2.0-x86_64.AppImage
   ```

Jeśli system nie obsługuje FUSE/AppImage:
```bash
./LinAmp-1.2.0-x86_64.AppImage --appimage-extract-and-run
```

AppImage zawiera LinAmp oraz potrzebne biblioteki (Python, PySide6, numpy,
mutagen) i jest przeznaczony dla systemów Linux **x86_64**.

### Opcja 2: Uruchomienie z folderu projektu (`run.sh`)

Potrzebujesz Pythona 3.10 lub nowszego.

1. Otwórz terminal w folderze z projektem.
2. Uruchom:
   ```bash
   ./run.sh
   ```
   Przy **pierwszym uruchomieniu** skrypt utworzy środowisko wirtualne i
   zainstaluje biblioteki (potrzebny internet, może potrwać kilka minut).
3. Kolejne uruchomienia są szybkie:
   ```bash
   ./run.sh
   ```

Jeśli środowisko Pythona było utworzone w innym systemie (np. wcześniej
w piaskownicy), `run.sh` wykryje to i sam je przebuduje.

### Skrót w menu aplikacji (opcjonalnie)

```bash
./install-linux.sh
```

Skrypt nie wymaga uprawnień administratora i dodaje LinAmp do menu „Dźwięk i
wideo” oraz (jeśli istnieje folder `Pulpit`/`Desktop`) skrót na pulpicie.

**Pierwsze uruchomienie z ikony może potrwać kilka minut**, jeśli środowisko
jest przygotowywane. Jeśli skrót na pulpicie nie reaguje, wybierz „Zezwól na
uruchamianie” (KDE/GNOME) lub użyj wpisu w menu aplikacji.

### Gdy `./run.sh` nie chce się uruchomić

Nadaj prawa wykonywania:
```bash
chmod +x run.sh install-linux.sh
```

Jeśli brakuje `venv`/`ensurepip`:
- Ubuntu/Debian: `sudo apt install python3-venv`
- Fedora: `sudo dnf install python3-pip`

Szczegóły błędów uruchamiania: `~/.local/state/LinAmp/launch.log`.

---

## Instalacja i uruchamianie na Windowsie

1. Zainstaluj Pythona ze strony <https://www.python.org/downloads/>.
   W instalatorze **zaznacz „Add python.exe to PATH”**.
2. Otwórz folder z projektem.
3. Uruchom **`run.bat`**.

Przy pierwszym uruchomieniu program pobierze biblioteki. Jeśli Windows pokaże
„Windows protected your PC”, wybierz **More info → Run anyway**.

---

## Jak korzystać

### Dodawanie muzyki

- **Dodaj pliki:** przycisk `+` lub `Ctrl+O`.
- **Dodaj folder:** przycisk folderu lub `Ctrl+Shift+O`.
- Możesz też **przeciągnąć pliki/foldery** na okno programu.

### Odtwarzanie

- Podwójne kliknięcie utworu lub `Enter` — odtwórz.
- `Space` (albo duży zielony przycisk) — odtwórz/pauza.
- `Z` / `B` — poprzedni / następny utwór.
- `V` — stop.
- `←` / `→` — przewiń o 5 s, `Shift + ←` / `→` — o 30 s.
- `↑` / `↓` — głośność, `M` — wyciszenie.
- `S` — losowo, `R` — powtarzanie.

### Playlista (M3U/M3U8/PLS)

- `Ctrl+S` — zapisz playlistę (wybierz format **M3U/M3U8** lub **PLS**).
- `Ctrl+L` — wczytaj playlistę.
- `F` — filtruj utwory, `Delete` — usuń zaznaczone z playlisty.
- Kliknięcie nagłówka kolumny sortuje listę.

### Korektor graficzny

- `Ctrl+E` lub **Narzędzia → Korektor…**.
- Włącz korektor, wybierz preset lub ustaw własne pasma (31 Hz–16 kHz) i preamp.
- Ustawienia są zapisywane i działają dla plików oraz radia.

### Radio internetowe

1. Kliknij **Radio** (`Ctrl+R`).
2. Wybierz kategorię (np. Rock, Jazz, Dance) lub **★ Ulubione** (`Ctrl+Shift+R`).
3. Dwukrotnie kliknij stację, aby odtworzyć.
4. Gwiazdka **☆/★** dodaje/usuwa stację z ulubionych.
5. Wyszukiwarka filtruje po nazwie, gatunku i aktualnej piosence.
6. **Nagrywanie:** odtwórz stację, kliknij **Nagraj**, a potem **Zatrzymaj nagrywanie**.

Podczas słuchania radia zamiast czasu widoczny jest napis **NA ŻYWO**, a
przewijanie jest wyłączone. Tytuł piosenki odświeża się automatycznie, gdy
stacja go udostępnia.

**Nagrania:** domyślnie zapisywane w folderze muzyki użytkownika w podfolderze
`LinAmp` (np. `Muzyka/LinAmp/Nagrania radiowe`). Jeśli w systemie jest dostępny
`ffmpeg`, nagranie zostanie zapisane jako MP3 (lub M4A); w przeciwnym razie jako
WAV. Radio wymaga połączenia z internetem. Lista stacji pochodzi z katalogu
[SHOUTcast](https://directory.shoutcast.com/).

### Język interfejsu

**Narzędzia → Język**: polski, angielski, niemiecki, francuski, hiszpański,
rosyjski. Po zmianie języka program uruchomi się ponownie, aby zastosować nowe
napisy.

---

## Skróty klawiszowe

| Klawisz | Działanie |
|---|---|
| `Space` | Odtwórz / pauza |
| `X` / `C` | Odtwórz / pauza (klasycznie, jak w Winampie) |
| `Z` / `B` | Poprzedni / następny utwór |
| `V` | Stop |
| `←` / `→` | Przewiń o 5 sekund |
| `Shift + ←` / `→` | Przewiń o 30 sekund |
| `↑` / `↓` | Głośność ±5% |
| `M` | Wycisz / włącz dźwięk |
| `S` | Tryb losowy |
| `R` | Tryb powtarzania |
| `F` | Filtruj playlistę |
| `Enter` | Odtwórz zaznaczony utwór |
| `Delete` | Usuń zaznaczone z playlisty |
| `Ctrl + O` | Otwórz pliki |
| `Ctrl + Shift + O` | Dodaj cały folder |
| `Ctrl + L` | Wczytaj playlistę (M3U/PLS) |
| `Ctrl + S` | Zapisz playlistę (M3U/PLS) |
| `Ctrl + R` | Otwórz radio internetowe |
| `Ctrl + Shift + R` | Otwórz ulubione stacje radiowe |
| `Ctrl + E` | Korektor graficzny |
| `F8` | Pokaż / ukryj playlistę |
| `F1` | Pomoc ze skrótami |
| `Ctrl + Q` | Zamknij program |

---

## Gdzie zapisywane są ustawienia

- **Linux:** `~/.config/LinAmp/state.json`
- **Windows:** `%APPDATA%\LinAmp\state.json`

Zapisywane są m.in. głośność, tryby odtwarzania, playlista, pozycja okna,
ulubione stacje radiowe, język, ustawienia korektora i folder nagrań. Plik można
usunąć — program utworzy nowy z wartościami domyślnymi. Ustawienia ze starej
nazwy `PyAmp` są migrowane automatycznie.

---

## Rozwiązywanie problemów

**Brak dźwięku**
- Sprawdź głośność w programie i w systemie.
- Naciśnij `M`, aby sprawdzić, czy dźwięk nie jest wyciszony.
- Na Linuksie sprawdź wybrane urządzenie wyjściowe w ustawieniach dźwięku.

**Radio się nie łączy lub nie gra**
- Sprawdź połączenie z internetem i kliknij **Odśwież**.
- Niektóre stacje bywają chwilowo niedostępne — spróbuj innej.

**Nagrywanie zapisuje WAV zamiast MP3**
- Zainstaluj `ffmpeg` w systemie (Linux: np. `sudo apt install ffmpeg` /
  `sudo dnf install ffmpeg`; Windows: dodaj `ffmpeg` do PATH). Bez FFmpeg
  nagranie jest zapisywane jako WAV.

**Korektor niedostępny**
- Korektor wymaga działającego urządzenia wyjściowego audio w systemie. Jeśli
  nie można go włączyć, odtwarzanie będzie działać normalnie bez korektora.

**Ikona w menu lub na pulpicie nie uruchamia programu (Linux)**
- Poczekaj przy pierwszym uruchomieniu (może potrwać kilka minut).
- Na pulpicie wybierz „Zezwól na uruchamianie” (jeśli wymagane).
- Sprawdź log: `~/.local/state/LinAmp/launch.log`.

**Błędy o brakujących bibliotekach Qt na Linuksie**
Na minimalnych instalacjach mogą być potrzebne biblioteki systemowe, np.:
- Fedora: `sudo dnf install krb5-libs pcsc-lite-libs keyutils-libs openssl-libs`
- Ubuntu/Debian: `sudo apt install libkrb5-3 libpcsclite1 libkeyutils1 libssl3`

**Muzyka się zacina**
- Zamknij inne obciążające programy i sprawdź, czy plik nie jest uszkodzony.
- Spróbuj wyłączyć korektor, aby porównać działanie.

---

## Struktura projektu

```text
linamp/
  __init__.py          nazwa i wersja aplikacji
  __main__.py          uruchamianie modułu (python -m linamp)
  app.py               punkt startowy
  audio.py             silnik odtwarzania i buforowanie próbek audio
  audioutil.py         konwersje próbek PCM (korektor, nagrywanie)
  config.py            zapis/odczyt ustawień JSON
  equalizer.py         10-pasmowy korektor graficzny
  i18n.py              tłumaczenia interfejsu (PL/EN/DE/FR/ES/RU)
  metadata.py          tagi, okładki, skanowanie folderów
  playlist.py          model playlisty, filtrowanie, M3U/PLS
  radio.py             katalog SHOUTcast i zadania sieciowe w tle
  recorder.py          nagrywanie radia (WAV + opcjonalna konwersja FFmpeg)
  theme.py             kolory i styl ciemnego interfejsu
  ui/
    main_window.py     główne okno i logika
    radio_window.py    okno radia (kategorie, ulubione, nagrywanie)
    equalizer_window.py  okno korektora
    controller.py      kolejność utworów, losowo, powtarzanie
    widgets.py         przyciski, suwaki, okładka
    spectrum.py        analizator widma
    icons.py           wektorowe ikony
    dialogs.py         pomoc i „O programie”
    workers.py         zadania w tle (metadane, okładki)
run.sh                 uruchamianie na Linuksie
run.bat                uruchamianie na Windowsie
install-linux.sh       skrót w menu Linuksa
dist/                  gotowe paczki (np. AppImage)
docs/                  zrzuty ekranu i ikona
requirements.txt       biblioteki Pythona
```

---

## Informacje techniczne

- Python 3.10+ i PySide6 (Qt 6) — jeden kod dla Linuksa i Windowsa.
- Odtwarzanie i dekodowanie: FFmpeg dołączony do PySide6.
- Tagi i okładki: mutagen.
- Widmo i przetwarzanie korektora: numpy (FFT).
- Radio: publiczne endpointy katalogu SHOUTcast, zapytania w tle (`QThreadPool`).
- Wersja: 1.2.0.

Miłego słuchania! 🎧
