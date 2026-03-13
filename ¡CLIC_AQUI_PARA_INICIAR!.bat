@echo off
TITLE PelisCristianas Bot - Cargador
cd /d "%~dp0"
powershell -ExecutionPolicy Bypass -File "IniciarBot.ps1"
pause
