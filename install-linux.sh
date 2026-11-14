#!/usr/bin/env bash
# Instaluje skrót LinAmp w menu aplikacji (bez uprawnień administratora).
# Uruchomienie:  ./install-linux.sh
set -e
cd "$(dirname "$0")"
PROJECT_DIR="$(pwd)"

chmod +x run.sh

# 1. Środowisko wirtualne i biblioteki (jednorazowo, ale zawsze sprawdzane).
# Używamy run.sh, żeby środowisko zostało utworzone tym Pythonem, który
# faktycznie uruchomi aplikację z ikony.
echo "Sprawdzam środowisko LinAmp…"
if ! bash "$PROJECT_DIR/run.sh" --setup-only; then
    echo
    echo "Nie udało się przygotować środowiska LinAmp."
    echo "Uruchom w terminalu:  $PROJECT_DIR/run.sh"
    echo "i przeczytaj komunikat błędu (jest też w ~/.local/state/LinAmp/launch.log)."
    exit 1
fi

# 2. Mały launcher bez spacji w ścieżce. Dzięki niemu wpis w menu nie
# zależy od poprawnego cytowania spacji w polu Exec.
BIN_DIR="$HOME/.local/bin"
mkdir -p "$BIN_DIR"
WRAPPER="$BIN_DIR/linamp"
cat > "$WRAPPER" <<EOF
#!/usr/bin/env bash
exec bash "$PROJECT_DIR/run.sh" "\$@"
EOF
chmod +x "$WRAPPER"

# 3. Ikona w standardowym katalogu (nazwa bez spacji i polskich znaków).
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
mkdir -p "$ICON_DIR"
cp docs/linamp.png "$ICON_DIR/linamp.png"

# 4. Wpis w menu aplikacji.
APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
DESKTOP_FILE="$APPS_DIR/linamp.desktop"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=LinAmp
GenericName=Odtwarzacz muzyki
Comment=Odtwarzacz muzyki i darmowe radio internetowe
Exec=$WRAPPER
TryExec=$WRAPPER
Icon=linamp
Terminal=false
Categories=AudioVideo;Audio;Player;
StartupNotify=true
StartupWMClass=LinAmp
X-KDE-Trusted=true
EOF

chmod +x "$DESKTOP_FILE"

# 5. Odświeżenie menu i ikon (jeśli system ma odpowiednie narzędzia).
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS_DIR" >/dev/null 2>&1 || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q "$HOME/.local/share/icons/hicolor" >/dev/null 2>&1 || true
fi
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 >/dev/null 2>&1 || true
elif command -v kbuildsycoca5 >/dev/null 2>&1; then
    kbuildsycoca5 >/dev/null 2>&1 || true
fi

# 6. Opcjonalny skrót na pulpicie (jeśli katalog istnieje).
for DESKTOP_DIR in "$HOME/Pulpit" "$HOME/Desktop"; do
    if [ -d "$DESKTOP_DIR" ]; then
        cp "$DESKTOP_FILE" "$DESKTOP_DIR/LinAmp.desktop"
        chmod +x "$DESKTOP_DIR/LinAmp.desktop"
        if command -v gio >/dev/null 2>&1; then
            gio set "$DESKTOP_DIR/LinAmp.desktop" metadata::trusted true >/dev/null 2>&1 || true
        fi
        echo "Dodano skrót na pulpicie: $DESKTOP_DIR/LinAmp.desktop"
        break
    fi
done

echo
echo "Gotowe! LinAmp jest teraz w menu aplikacji (kategoria: Dźwięk i wideo)."
echo "Możesz też uruchamiać go poleceniem:  $PROJECT_DIR/run.sh"
