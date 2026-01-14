@echo off
echo ==========================================
echo       INITIALISATION DE JARVIS
echo ==========================================

echo [1/3] Verification des dependances...
python -m pip install -r requirements.txt > nul
if %errorlevel% neq 0 (
    echo Erreur lors de l'installation des dependances.
    pause
    exit /b
)
echo Dependances OK.

echo [2/3] Verification de Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I /N "ollama.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo Ollama est deja lance.
) else (
    echo Ollama n'est pas lance. Jarvis tentera de le demarrer...
)

echo [3/3] Lancement de Jarvis...
python main.py

pause
