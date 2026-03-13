# Script de inicio para PelisCristianas Bot
# Configura la ruta al directorio del script
Set-Location -Path $PSScriptRoot

Clear-Host
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "     INICIANDO PELIS CRISTIANAS BOT V4.0 (TORRENTS)     " -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

# Intentar activar el entorno virtual si existe
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "[*] Activando entorno virtual..." -ForegroundColor Yellow
    & ".\venv\Scripts\Activate.ps1"
}

# Verificar si python está instalado
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[!] ERROR: Python no está instalado o no está en el PATH." -ForegroundColor Red
    Pause
    exit
}

# Ejecutar el bot
Write-Host "[*] Lanzando motor principal..." -ForegroundColor Green
python main.py

# Si el bot se cierra, mantener la ventana abierta para ver errores
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Proceso finalizado. Presiona cualquier tecla para cerrar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
