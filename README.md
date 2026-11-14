# LinAmp

LinAmp to prosty odtwarzacz muzyki i radia internetowego dla systemu Linux i Windows. Wyglądem i obsługą nawiązuje do klasycznych odtwarzaczy, a do działania wykorzystuje Pythona i biblioteki PySide6 (Qt), Qt Multimedia/FFmpeg, mutagen i numpy.

## Najważniejsze możliwości

- **Odtwarzanie muzyki**: MP3, FLAC, OGG/Opus, WAV, M4A/AAC, WMA, APE, WavPack, AIFF i inne formaty obsługiwane przez Qt Multimedia/FFmpeg.
- **Tryby odtwarzania** (jeden przycisk/menu, zapamiętywany):
  - **Po kolei** — odtwarza utwory w widocznej kolejności i zatrzymuje się po ostatnim,
  - **W pętli** — odtwarza całą listę w kółko,
  - **Losowo** — tasuje kolejność odtwarzania i gra dalej losowo.
- **Playlista**: dodawanie plików i folderów (także przeciągnij i upuść), wyszukiwanie, sortowanie kolumn, zapamiętywanie stanu, przycisk **„Wyczyść listę”**. Kolejność odtwarzania w trybach nielosowych uwzględnia aktualne sortowanie/widok listy.
- **Informacje o utworach** na liście: tytuł, wykonawca, album, **rok/data**, czas, **kodek** i **bitrate** (uzupełniane po odczycie metadanych). Aktualnie odtwarzany utwór jest wyraźnie podświetlany na zielono.
- **Playlisty**: wczytywanie i zapisywanie w formatach **M3U / M3U8 / PLS**.
- **Radio internetowe**: darmowe stacje z katalogu SHOUTcast (bez rejestracji i bez klucza API), ulubione stacje, informacja o aktualnie granej piosence.
- **Nagrywanie radia**: zapis do pliku (WAV; jeśli FFmpeg jest dostępny — także konwersja do MP3/M4A).
- **Korektor graficzny 10 pasm** (31 Hz – 16 kHz), presety i regulacja preamp.
- **Analizator widma**.
- **Okładki**: osadzone w plikach i znalezione w folderze utworu/albumu (także w folderach nadrzędnych, np. przy podfolderach `CD1`/`Volume 1`); gdy lokalna okładka jest niedostępna, LinAmp próbuje pobrać ją z internetu na podstawie metadanych (wymagane połączenie sieciowe).
- **4 skórki wyglądu**: Ciemna, Jasna, Niebieska i Bursztynowa (**Widok → Wygląd**).
- **6 języków interfejsu**: polski, angielski, niemiecki, francuski, hiszpański i rosyjski (**Narzędzia → Język**).
- **Wygoda**: ikona w zasobniku systemowym, skróty klawiszowe i multimedialne, zapamiętywanie głośności, trybu odtwarzania, pozycji okna i listy.

## Pobieranie i instalacja

W katalogu `dist/` dostępne są pakiety dla wersji **1.2.0** (z aktualnymi poprawkami odtwarzania, kolejki i sortowania):

| Plik | System | Opis |
|---|---|---|
| `LinAmp-1.2.0-amd64.deb` | Debian / Ubuntu / Linux Mint | Pakiet `.deb` (amd64). Instaluje program w `/opt/linamp`, dodaje skrót w menu i ikonę. |
| `LinAmp.spec` | Fedora / RHEL / openSUSE | Plik spec do zbudowania pakietu `.rpm` (instrukcja poniżej). |
| `LinAmp-1.2.0-x86_64.AppImage` | Linux (uniwersalny) | Przenośny AppImage, bez instalacji. *Uwaga: może wymagać przebudowania, aby zawierać najnowsze poprawki ze źródeł.* |
| `LinAmp-1.2.0-linux-portable.tar.gz` | Linux | Wersja przenośna (źródła + skrypty uruchomieniowe). |
| `LinAmp-1.2.0-windows-portable.zip` | Windows | Wersja przenośna dla Windows (instrukcja poniżej). |

> **Uwaga o formatach:** w tym środowisku nie było narzędzi do zbudowania binarnego `.rpm` (`rpmbuild`) ani natywnego instalatora `.exe` dla Windows — dla Fedory/RHEL dostarczony jest `.spec` i paczka przenośna, dla Windows paczka `.zip` z `run.bat`. Instalator `.exe` można przygotować na Windows (np. PyInstaller + Inno Setup).

### Debian / Ubuntu (.deb)

```bash
sudo apt install ./dist/LinAmp-1.2.0-amd64.deb
```

Zależności: `python3 (>= 3.10)`, `python3-venv`, `python3-pip`, `ffmpeg`. Przy pierwszym uruchomieniu program utworzy środowisko i doinstaluje biblioteki Pythona (wymagane połączenie z internetem).

### Fedora / RHEL (.rpm)

Zbuduj pakiet z `dist/LinAmp.spec` na systemie z `rpmbuild` (używając źródeł/paczki zgodnie z sekcją `%install`), np. `rpmbuild -bb dist/LinAmp.spec`. Alternatywnie użyj wersji przenośnej: rozpakuj `LinAmp-1.2.0-linux-portable.tar.gz` i uruchom `./run.sh`.

### Linux — AppImage

```bash
chmod +x dist/LinAmp-1.2.0-x86_64.AppImage
./dist/LinAmp-1.2.0-x86_64.AppImage
```

Nie wymaga instalacji. Jeśli chcesz mieć pewność najnowszych poprawek ze źródeł, użyj przebudowanego AppImage lub paczki `.deb`/przenośnej.

### Windows — paczka przenośna (.zip)

1. Zainstaluj **Python 3.10 lub nowszy**: https://www.python.org/downloads/ (zaznacz **„Add Python to PATH”**).
2. Rozpakuj `dist/LinAmp-1.2.0-windows-portable.zip` (np. `C:\Programy\LinAmp`).
3. Uruchom **`run.bat`** — przy pierwszym uruchomieniu powstanie `.venv` i zostaną pobrane biblioteki (wymagane połączenie z internetem).
4. (Opcjonalnie) utwórz skrót do `run.bat`.

Aby nagrywać radio do MP3/M4A, zainstaluj **FFmpeg** i dodaj go do `PATH` (bez FFmpeg nagrania są w WAV).

### Uruchomienie ze źródeł (Linux)

```bash
./run.sh
```

Skrypt tworzy/naprawia środowisko `.venv` i uruchamia `python -m linamp`. Można podać pliki/foldery jako argumenty, np. `./run.sh ~/Muzyka`.

**Pełny projekt z najnowszymi aktualizacjami odtwarzacza LinAmp 1.2.0 wraz z plikami instalacyjnymi pobierzesz z Proton**: (https://drive.proton.me/urls/G3ATX7TDTR#WLDunQbdDtUU)
## Obsługa

### Tryby odtwarzania i kolejka
- **Po kolei** — gra w kolejności widocznej na liście i zatrzymuje się na końcu.
- **W pętli** — powtarza całą listę.
- **Losowo** — losowa kolejność utworów.
- Przełączanie: przycisk trybu lub menu **Odtwarzanie**. Skróty: `R` (następny tryb), `S` (losowo), `L` (w pętli), `Shift+L` (po kolei).
- Sortowanie listy (klik w nagłówek kolumny) wpływa na kolejność odtwarzania w trybach nielosowych.

### Playlista i pliki
- Dodawanie: `Ctrl+O` (pliki), `Ctrl+Shift+O` (folder), przeciągnij i upuść.
- Wczytaj/zapisz playlistę **M3U/M3U8/PLS**: `Ctrl+L` / `Ctrl+S`.
- **Wyczyść listę** — przycisk na pasku playlisty (z potwierdzeniem). `Delete` usuwa zaznaczone.
- Filtruj: `F`. Kolumny: tytuł, wykonawca, album, rok/data, czas, kodek, bitrate.

### Radio, korektor, wygląd
- **Radio internetowe**: `Ctrl+R`, ulubione: `Ctrl+Shift+R`; nagrywanie w oknie radia (WAV/MP3/M4A z FFmpeg).
- **Korektor graficzny**: `Ctrl+E` (10 pasm, presety, preamp).
- **Skórki**: **Widok → Wygląd** (Ciemna/Jasna/Niebieska/Bursztynowa), restart po zmianie.
- **Język**: **Narzędzia → Język** (PL/EN/DE/FR/ES/RU), restart po zmianie.

### Skróty klawiszowe (najważniejsze)
- `Spacja` / `X` / `C` / `V` – odtwórz/pauza, odtwórz, pauza, stop
- `Z` / `B` – poprzedni / następny utwór
- `←` / `→` – przewiń 5 s, `Shift+←/→` – 30 s
- `↑` / `↓` – głośniej/ciszej, `M` – wycisz
- `R` – zmień tryb odtwarzania, `S` – losowo, `L` – w pętli, `Shift+L` – po kolei
- `F` – filtruj, `Delete` – usuń zaznaczone
- `Ctrl+O` / `Ctrl+Shift+O` – dodaj pliki / folder
- `Ctrl+L` / `Ctrl+S` – wczytaj / zapisz playlistę (M3U/PLS)
- `Ctrl+R` / `Ctrl+Shift+R` – radio / ulubione stacje
- `Ctrl+E` – korektor, `F8` – pokaż/ukryj playlistę, `F1` – pomoc

## Gdzie zapisywane są dane

- **Ustawienia i stan**: `~/.config/LinAmp/state.json` (Linux) lub `%APPDATA%\LinAmp\state.json` (Windows). Starsza konfiguracja `PyAmp` jest migrowana automatycznie.
- **Nagrania radiowe** (domyślnie): katalog Muzyka → `LinAmp/Nagrania radiowe`.
- **Log uruchamiania** (Linux, `run.sh`): `~/.local/state/LinAmp/launch.log`.

## Rozwiązywanie problemów

- **Brak dźwięku / format nie działa**: zainstaluj kodeki obsługiwane przez Qt Multimedia (np. GStreamer/FFmpeg).
- **Nagrywanie do MP3/M4A niedostępne**: zainstaluj `ffmpeg` (bez niego nagrania są w WAV).
- **Korektor niedostępny**: zależy od backendu audio Qt na danym systemie.
- **Brak okładki**: wyświetlane są okładki osadzone i z plików w folderze/albumie; przy ich braku LinAmp próbuje pobrać okładkę z internetu (wymaga sieci i poprawnych metadanych).
- **Zmiana języka/skórki niewidoczna od razu**: po potwierdzeniu program uruchamia się ponownie.
- **Radio nie łączy się**: sprawdź internet; wybrane strumienie mogą być chwilowo niedostępne.

## Uwagi

- Paczka `.deb` instaluje program do `/opt/linamp` i przy pierwszym uruchomieniu może doinstalować zależności Pythona (venv/pip) — wymagane połączenie z internetem.
- Planowane dalej: m.in. rozszerzenia obsługi playlist (np. `.cue`) i kolejne ulepszenia metadanych.
