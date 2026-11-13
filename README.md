# LinAmp
Nowoczesny odtwarzacz muzyczny inspirowany Winampem — z darmowym radiem internetowym i ponad 300 kategoriami. Działa na Linuksie i Windowsie, a interfejs jest w całości po polsku.

# LinAmp 🎵

Nowoczesny odtwarzacz muzyczny inspirowany Winampem — z **darmowym radiem
internetowym** i ponad 300 kategoriami. Działa na **Linuksie** i **Windowsie**,
a interfejs jest w całości po polsku.

![Okno główne LinAmp](docs/okno-glowne.png)

## Najważniejsze funkcje

- Odtwarzanie MP3, FLAC, OGG/Opus, WAV, M4A/AAC, WMA i innych formatów
  obsługiwanych przez FFmpeg.
- Playlista z filtrowaniem, sortowaniem, zapisem i wczytywaniem M3U/M3U8.
- Przewijanie, głośność, wyciszenie, tryb losowy i powtarzanie.
- Prawdziwy analizator widma (FFT) reagujący na muzykę.
- Okładki i tagi (tytuł, wykonawca, album).
- Zasobnik systemowy i obsługa klawiszy multimedialnych.
- **Radio internetowe SHOUTcast** — bez rejestracji i bez klucza API:
  kategorie, wyszukiwanie, sortowanie, ulubione stacje i podgląd tego, co gra.

![Okno radia](docs/radio.png)

---

## Instalacja na Linuksie (zalecane)

Potrzebujesz Pythona 3.10 lub nowszego (na Fedorze i Ubuntu jest zwykle
zainstalowany).

1. Otwórz terminal w folderze z projektem.
2. Uruchom:

   ```bash
   ./run.sh
   ```

   Przy **pierwszym uruchomieniu** program sam utworzy środowisko wirtualne
   i zainstaluje potrzebne biblioteki. Potrwa to kilka minut — potrzeba
   połączenia z internetem.
3. Kolejne uruchomienia są już szybkie:

   ```bash
   ./run.sh
   ```

### Skrót w menu aplikacji (opcjonalnie)

Aby LinAmp pojawił się w menu „Dźwięk i wideo” (i ewentualnie na pulpicie):

```bash
./install-linux.sh
```

Skrypt nie wymaga uprawnień administratora i niczego nie instaluje poza
skrótem. Program nadal uruchamia się z tego folderu.

Po instalacji LinAmp pojawia się w menu aplikacji (kategoria „Dźwięk i wideo”)
oraz — jeśli istnieje folder `Pulpit` lub `Desktop` — jako skrót na pulpicie.

**Pierwsze kliknięcie ikony może potrwać kilka minut**, jeśli program musi
przygotować środowisko Pythona na Twoim systemie. Kolejne uruchomienia są
szybkie.

Jeśli skrót na pulpicie nie reaguje, kliknij go prawym przyciskiem myszy
i wybierz **„Zezwól na uruchamianie”** (KDE/GNOME) — albo skorzystaj z wpisu
w menu aplikacji, który nie wymaga potwierdzania.

### Gdy `./run.sh` nie chce się uruchomić

Nadaj plikowi prawo wykonywania:

```bash
chmod +x run.sh install-linux.sh
```

Jeśli pojawi się błąd o brakującym `venv` lub `ensurepip`:

- Ubuntu/Debian: `sudo apt install python3-venv`
- Fedora: `sudo dnf install python3-pip`

Na Windowsie, jeśli `run.bat` nie znajduje Pythona, uruchom instalator Pythona
ponownie i zaznacz **„Add python.exe to PATH”**.

---

## Instalacja na Windowsie

1. Zainstaluj Pythona ze strony <https://www.python.org/downloads/>.
   W instalatorze **zaznacz „Add python.exe to PATH”**.
2. Otwórz folder z projektem.
3. Kliknij dwukrotnie **`run.bat`**.

Przy pierwszym uruchomieniu otworzy się okno terminala, które samo pobierze
biblioteki.Po chwili pojawi się odtwarzacz. Kolejne uruchomienia są szybsze.

> Jeśli Windows pokaże niebieski komunikat „Windows protected your PC”,
> kliknij **More info → Run anyway**. To normalne dla plików .bat
> pobranych z internetu.

---

## Jak korzystać

### Dodawanie muzyki

- **Dodaj pliki** — przycisk `+` albo `Ctrl+O`.
- **Dodaj cały folder** — przycisk folderu albo `Ctrl+Shift+O`.
- Możesz też **przeciągnąć pliki lub foldery** myszką na okno programu.

### Odtwarzanie

- Kliknij dwukrotnie utwór na playliście albo naciśnij `Enter`.
- Duży zielony przycisk lub `Space` — odtwarzanie / pauza.
- `Z` / `B` — poprzedni / następny utwór.
- `←` / `→` — przewiń o 5 sekund, z `Shift` — o 30 sekund.
- `S` — tryb losowy, `R` — powtarzanie, `M` — wyciszenie.

### Radio internetowe

1. Kliknij przycisk **Radio** w prawym górnym rogu (albo `Ctrl+R`).
2. Wybierz kategorię z listy po lewej (np. Rock, Jazz, Dance).
3. Kliknij dwukrotnie stację — zacznie grać.
4. Gwiazdką **☆ Dodaj do ulubionych** zapiszesz stację na później.
   Ulubione otworzysz przez `Ctrl+Shift+R`.
5. Pole wyszukiwania filtruje po nazwie stacji, gatunku i aktualnej piosence.
6. Kliknięcie nagłówka kolumny sortuje tabelę (np. według liczby słuchaczy).

Podczas słuchania radia:

- zamiast czasu utworu widzisz **NA ŻYWO**,
- przewijanie jest wyłączone (radio gra na żywo),
- tytuł piosenki odświeża się automatycznie, gdy stacja go udostępnia,
- możesz dalej korzystać z playlisty — wybranie utworu automatycznie
  przełączy odtwarzanie z radia na muzykę.

Radio wymaga połączenia z internetem. Lista stacji pochodzi z publicznego
katalogu [SHOUTcast](https://directory.shoutcast.com/).

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
| `Ctrl + L` | Wczytaj playlistę (M3U) |
| `Ctrl + S` | Zapisz playlistę (M3U) |
| `Ctrl + R` | Otwórz radio |
| `Ctrl + Shift + R` | Otwórz ulubione stacje |
| `F8` | Pokaż / ukryj playlistę |
| `F1` | Pomoc ze skrótami |
| `Ctrl + Q` | Zamknij program |

---

## Gdzie zapisywane są ustawienia

- **Linux:** `~/.config/LinAmp/state.json`
- **Windows:** `%APPDATA%\LinAmp\state.json`

Plik zawiera głośność, tryby odtwarzania, playlistę, rozmiar okna i ulubione
stacje radiowe. Możesz go usunąć — program utworzy nowy z ustawieniami
domyślnymi. Ustawienia ze starej nazwy `PyAmp` są przenoszone automatycznie.

---

## Rozwiązywanie problemów

**Brak dźwięku**

- Sprawdź głośność w programie i w systemie.
- Kliknij ikonę głośnika (`M`), aby upewnić się, że dźwięk nie jest wyciszony.
- Na Linuksie sprawdź, czy wybrane jest właściwe urządzenie wyjściowe
  (np. w ustawieniach dźwięku KDE/GNOME).

**Radio się nie łączy**

- Upewnij się, że masz internet.
- Kliknij **Odśwież** w oknie radia.
- Niektóre stacje bywają chwilowo niedostępne — spróbuj innej.

**Ikona w menu lub na pulpicie nie uruchamia programu**

- Pierwsze uruchomienie może potrwać kilka minut — poczekaj i nie klikaj
  wielokrotnie.
- Spróbuj wpisu w menu aplikacji zamiast skrótu na pulpicie.
- Jeśli na pulpicie pojawi się pytanie o zaufanie, wybierz
  **„Zezwól na uruchamianie”**.
- Dokładny powód błędu jest zapisywany w pliku:

  ```text
  ~/.local/state/LinAmp/launch.log
  ```

  Ostatnie linie tego pliku wystarczą, żeby ustalić przyczynę.

**Komunikat o brakującej bibliotece `.so` na Linuksie**

Na minimalnych instalacjach może brakować bibliotek systemowych wymaganych
przez Qt. Na Fedorze:

```bash
sudo dnf install krb5-libs pcsc-lite-libs keyutils-libs openssl-libs
```

Na Ubuntu/Debian:

```bash
sudo apt install libkrb5-3 libpcsclite1 libkeyutils1 libssl3
```

**Muzyka się zacina**

- Zamknij inne wymagające programy.
- Sprawdź, czy plik nie jest uszkodzony (odtwórz go w innym programie).
- Widmo i odtwarzanie korzystają z FFmpeg dołączonego do PySide6 — nie
  trzeba instalować go osobno.

---

## Struktura projektu

```
linamp/
  __init__.py        nazwa i wersja aplikacji
  app.py             punkt startowy
  audio.py           silnik odtwarzania (QMediaPlayer + próbki do widma)
  config.py          zapis/odczyt ustawień JSON
  metadata.py        tagi, okładki, skanowanie folderów
  playlist.py        model playlisty, filtrowanie, M3U
  radio.py           katalog SHOUTcast i zadania sieciowe w tle
  theme.py           kolory i styl ciemnego interfejsu
  ui/
    main_window.py   główne okno i logika
    radio_window.py  okno radia (kategorie, ulubione, wyszukiwanie)
    controller.py    kolejność utworów, losowo, powtarzanie
    widgets.py       przyciski, suwaki, okładka
    spectrum.py      analizator widma
    icons.py         wektorowe ikony
    dialogs.py       pomoc i „O programie”
run.sh               uruchamianie na Linuksie
run.bat              uruchamianie na Windowsie
install-linux.sh     skrót w menu Linuksa
requirements.txt     biblioteki Pythona
docs/                zrzuty ekranu i ikona
```

---

## Informacje techniczne

- Python 3.10+ i PySide6 (Qt 6) — jeden kod dla Linuksa i Windowsa.
- Odtwarzanie i dekodowanie: FFmpeg dołączony do PySide6.
- Tagi i okładki: mutagen.
- Widmo: numpy (szybka transformata Fouriera).
- Radio: publiczne endpointy katalogu SHOUTcast, zapytania w tle
  (`QThreadPool`), więc interfejs nigdy się nie zacina.

Miłego słuchania! 🎧
