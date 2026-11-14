#!/usr/bin/env bash
# Uruchamia LinAmp.
#
# Przy pierwszym uruchomieniu (lub po zmianie wersji Pythona) tworzy
# środowisko wirtualne i instaluje biblioteki. Dzięki temu ikona w menu
# działa również wtedy, gdy projekt był wcześniej uruchamiany w innym
# środowisku (np. w piaskownicy Flatpak).
set -u

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || exit 1

# --- logowanie -----------------------------------------------------------
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/LinAmp"
if ! mkdir -p "$STATE_DIR" 2>/dev/null || ! touch "$STATE_DIR/launch.log" 2>/dev/null; then
    STATE_DIR="${TMPDIR:-/tmp}/LinAmp-${USER:-user}"
    mkdir -p "$STATE_DIR" 2>/dev/null || true
fi
LOG="$STATE_DIR/launch.log"
touch "$LOG" 2>/dev/null || LOG=/dev/null

# W terminalu pokazujemy komunikaty na ekranie; z ikony zapisujemy je do logu.
if [ -t 2 ]; then
    exec > >(tee -a "$LOG") 2>&1
else
    exec >>"$LOG" 2>&1
fi

echo
echo "=== $(date '+%Y-%m-%d %H:%M:%S') LinAmp ==="
echo "Projekt: $PROJECT_DIR"
echo "System: $(uname -a 2>/dev/null || true)"

# --- komunikaty graficzne ------------------------------------------------
dialog_error() {
    local message="$1"
    echo "BŁĄD: $message" >&2
    if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
        if command -v kdialog >/dev/null 2>&1; then
            kdialog --title "LinAmp" --error "$message" >/dev/null 2>&1 || true
        elif command -v zenity >/dev/null 2>&1; then
            zenity --error --title="LinAmp" --text="$message" >/dev/null 2>&1 || true
        elif command -v notify-send >/dev/null 2>&1; then
            notify-send -u critical "LinAmp" "$message" >/dev/null 2>&1 || true
        fi
    fi
}

dialog_info() {
    local message="$1"
    if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then
        if command -v kdialog >/dev/null 2>&1; then
            kdialog --title "LinAmp" --passivepopup "$message" 10 >/dev/null 2>&1 &
        elif command -v zenity >/dev/null 2>&1; then
            zenity --info --title="LinAmp" --text="$message" --timeout=10 >/dev/null 2>&1 &
        elif command -v notify-send >/dev/null 2>&1; then
            notify-send "LinAmp" "$message" >/dev/null 2>&1 || true
        fi
    fi
}

# --- wybór Pythona gospodarza -------------------------------------------
python_version_ok() {
    "$1" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1
}

HOST_PYTHON=""
for candidate in python3 python3.14 python3.13 python3.12 python3.11 python3.10 python; do
    if command -v "$candidate" >/dev/null 2>&1 && python_version_ok "$candidate"; then
        HOST_PYTHON="$candidate"
        break
    fi
done

if [ -z "$HOST_PYTHON" ]; then
    dialog_error "Nie znaleziono Pythona 3.10 lub nowszego.

Zainstaluj Pythona 3 ze strony https://www.python.org/downloads/
lub z menedżera pakietów swojego systemu, a następnie kliknij ikonę LinAmp ponownie.

Szczegóły: $LOG"
    exit 1
fi

HOST_VERSION="$("$HOST_PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "?")"
echo "Python: $HOST_PYTHON ($HOST_VERSION)"

# Pełny import aplikacji sprawdza też biblioteki Qt (Multimedia, Network).
qt_import_error() {
    .venv/bin/python -c 'from linamp.app import main' 2>&1
}

missing_library_from_error() {
    printf '%s\n' "$1" | sed -n 's/.*ImportError: \([^:]*\): cannot open shared object file.*/\1/p' | head -1
}

show_qt_library_error() {
    local details="$1"
    local missing
    missing="$(missing_library_from_error "$details")"
    if [ -n "$missing" ]; then
        dialog_error "LinAmp nie może załadować biblioteki systemowej:
$missing

Na Fedorze uruchom:
sudo dnf install krb5-libs pcsc-lite-libs keyutils-libs openssl-libs

Na Ubuntu/Debian:
sudo apt install libkrb5-3 libpcsclite1 libkeyutils1 libssl3

Potem kliknij ikonę LinAmp ponownie.
Szczegóły: $LOG"
    else
        dialog_error "LinAmp nie może załadować bibliotek Qt.

Szczegóły znajdują się w pliku:
$LOG"
    fi
}

# --- sprawdzenie istniejącego środowiska --------------------------------
venv_ok=0
venv_version="?"
modules_present=0

if [ -x ".venv/bin/python" ]; then
    venv_version="$(.venv/bin/python -c 'import sys; print("%d.%d" % sys.version_info[:2])' 2>/dev/null || echo "?")"
    echo "Środowisko .venv: Python $venv_version"

    modules_present=1
    for module in PySide6 mutagen numpy; do
        if ! .venv/bin/python -c "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('$module') else 1)" >/dev/null 2>&1; then
            modules_present=0
            echo "Brak modułu w .venv: $module"
        fi
    done

    if [ "$venv_version" = "$HOST_VERSION" ] && [ "$modules_present" -eq 1 ]; then
        if .venv/bin/python -c 'from linamp.app import main' >/dev/null 2>&1; then
            venv_ok=1
        else
            # Moduły są, ale nie da się ich zaimportować — zwykle brakuje
            # bibliotek systemowych. Nie przebudowujemy środowiska w kółko.
            venv_ok=2
        fi
    fi
fi

# --- przygotowanie środowiska -------------------------------------------
build_venv() {
    local new_dir=".venv.new.$$"

    dialog_info "Przygotowuję LinAmp. To może potrwać kilka minut — potrzebne jest połączenie z internetem."
    echo "Tworzę nowe środowisko: $new_dir (Python $HOST_VERSION)"

    rm -rf "$new_dir"
    if ! "$HOST_PYTHON" -m venv "$new_dir"; then
        rm -rf "$new_dir"
        dialog_error "Nie udało się utworzyć środowiska Pythona.

Na Ubuntu/Debian zainstaluj: sudo apt install python3-venv
Na Fedorze: sudo dnf install python3-pip

Szczegóły: $LOG"
        exit 1
    fi

    if ! "$new_dir/bin/python" -m pip install --upgrade pip; then
        rm -rf "$new_dir"
        dialog_error "Nie udało się pobrać narzędzia pip. Sprawdź połączenie z internetem.

Szczegóły: $LOG"
        exit 1
    fi

    if ! "$new_dir/bin/python" -m pip install -r requirements.txt; then
        rm -rf "$new_dir"
        dialog_error "Nie udało się zainstalować bibliotek LinAmp. Sprawdź połączenie z internetem.

Szczegóły: $LOG"
        exit 1
    fi

    rm -rf .venv
    if ! mv "$new_dir" .venv; then
        dialog_error "Nie udało się zainstalować środowiska LinAmp.

Szczegóły: $LOG"
        exit 1
    fi
}

if [ "$venv_ok" -eq 2 ]; then
    details="$(qt_import_error)"
    show_qt_library_error "$details"
    exit 1
fi

if [ "$venv_ok" -ne 1 ]; then
    build_venv
fi

# --- weryfikacja końcowa -------------------------------------------------
details="$(qt_import_error)"
qt_status=$?
if [ "$qt_status" -ne 0 ]; then
    show_qt_library_error "$details"
    exit 1
fi

# Tryb używany przez install-linux.sh — tylko przygotowanie środowiska.
if [ "${1:-}" = "--setup-only" ]; then
    echo "Środowisko LinAmp jest gotowe."
    exit 0
fi

# --- uruchomienie --------------------------------------------------------
echo "Uruchamiam LinAmp..."
.venv/bin/python -m linamp "$@"
status=$?

if [ "$status" -ne 0 ]; then
    dialog_error "LinAmp zakończył się błędem (kod $status).

Szczegóły: $LOG"
fi

exit "$status"
