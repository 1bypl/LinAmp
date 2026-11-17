# LinAmp 1.2.0 dla Windows

LinAmp to odtwarzacz muzyki i radia internetowego. Wersja Windows jest
przygotowana dla systemów Windows 10/11 64-bit.

## Instalacja

1. Pobierz `LinAmp-1.2.0-Setup.exe` z katalogu `dist`.
2. Uruchom instalator i wybierz opcjonalnie utworzenie skrótu na pulpicie.
3. Uruchom LinAmp z menu Start lub skrótu na pulpicie.

Instalator nie wymaga osobnej instalacji Pythona ani FFmpeg. FFmpeg jest
opcjonalny i potrzebny do konwersji nagrań radia do MP3/M4A; bez niego
nagrania są zapisywane jako WAV.

Ustawienia programu znajdują się w `%APPDATA%\LinAmp\state.json`, a nagrania
domyślnie w folderze Muzyka\LinAmp\Nagrania radiowe.

## Wersja przenośna

Alternatywnie rozpakuj `dist\LinAmp-1.2.0-windows-portable.zip`, zainstaluj
Python 3.10 lub nowszy i uruchom `run.bat`. Przy pierwszym uruchomieniu
wymagane jest połączenie z internetem do pobrania zależności.

## Budowanie instalatora ze źródeł

Na Windows zainstaluj Python 3.10+ oraz Inno Setup 6. W katalogu projektu
uruchom PowerShell:

```powershell
.\build-windows.ps1
```

Skrypt instaluje zależności Pythona, buduje aplikację przez PyInstaller,
a następnie tworzy `dist\LinAmp-1.2.0-Setup.exe` za pomocą Inno Setup.
Wymagane jest połączenie z internetem podczas pierwszego budowania.

## Informacje o programie

- Wersja: 1.2.0
- Systemy: Linux (Debian/Ubuntu i Fedora) oraz Windows 10/11 (64-bit)
- Licencja: GNU General Public License v3 (GPL-3.0)
- Twórca: [1bypl na GitHub](https://github.com/1bypl)
