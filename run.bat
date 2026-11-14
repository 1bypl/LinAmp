@echo off
rem Uruchamia LinAmp na Windowsie. Pierwsze uruchomienie tworzy srodowisko
rem wirtualne i instaluje biblioteki.
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo First run: creating virtual environment and installing packages...
    py -3 -m venv .venv 2>nul || python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    echo Done.
)

.venv\Scripts\python.exe -m linamp %*
