@echo off
cls
echo === NetPulse Build Script ===

echo [1/5] Pulizia build precedente...
rmdir /s /q dist >nul 2>&1
rmdir /s /q build >nul 2>&1
del /q netpulse_launcher.spec >nul 2>&1

echo [2/5] Compilazione launcher (NO onefile)...
pyinstaller --windowed netpulse_launcher.py

echo [3/5] Copia dei file aggiornabili...
copy main.py dist\netpulse_launcher\ >nul
copy netpulse.py dist\netpulse_launcher\ >nul
copy netpulsegui.py dist\netpulse_launcher\ >nul
copy netpulsetheme.py dist\netpulse_launcher\ >nul

echo [4/5] Verifica contenuto finale:
IF NOT EXIST dist\netpulse_launcher\netpulse_launcher.exe echo [ERRORE] .exe non trovato
IF NOT EXIST dist\netpulse_launcher\main.py echo [ERRORE] main.py mancante
IF NOT EXIST dist\netpulse_launcher\netpulse.py echo [ERRORE] netpulse.py mancante

echo [5/5] Build completata. Pronto per lanciare o impacchettare.
echo Cartella finale: dist\netpulse_launcher\
echo.
pause