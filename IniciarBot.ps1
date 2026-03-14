# =========================================================
# UNIVERSAL MEDIA BOT - AUTO-INSTALADOR Y LANZADOR (V4.0)
# =========================================================

Set-Location -Path $PSScriptRoot
Clear-Host

Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "       UMO-CORE: INICIANDO ASISTENTE DE ARRANQUE        " -ForegroundColor Cyan
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

# 1. Comprobar instalación de Python
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[X] ERROR CRÍTICO: Python no está instalado en este equipo." -ForegroundColor Red
    Write-Host "Para que el Bot funcione, DEBES instalar Python 3.10 o superior." -ForegroundColor Yellow
    Write-Host "=> Link de descarga: https://www.python.org/downloads/" -ForegroundColor Magenta
    Write-Host "IMPORTANTE: Al instalar Python, marca la casilla 'Add python.exe to PATH'." -ForegroundColor Yellow
    Pause
    exit
}

# 2. Crear archivo .env si es la primera vez (Cliente nuevo)
if (!(Test-Path ".\.env")) {
    Write-Host "[*] Detectado un usuario nuevo. Creando configuración inicial (.env)..." -ForegroundColor Yellow
    Copy-Item ".\.env.example" -Destination ".\.env"
    Write-Host "[OK] Archivo '.env' creado. Puedes editarlo luego para configurar qBittorrent." -ForegroundColor Green
}

# 3. Comprobar / Crear Entorno Virtual
if (!(Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "[*] Configurando el motor por primera vez (Esto puede tardar unos minutos)..." -ForegroundColor Yellow
    Write-Host "    -> Creando Entorno Virtual..." -ForegroundColor Cyan
    python -m venv venv
    
    if (!(Test-Path ".\venv\Scripts\Activate.ps1")) {
        Write-Host "[X] Error al crear el entorno virtual. Contacta con soporte." -ForegroundColor Red
        Pause
        exit
    }
}

# 4. Activar Entorno e Instalar Dependencias
Write-Host "[*] Activando sistema..." -ForegroundColor Cyan
& ".\venv\Scripts\Activate.ps1"

Write-Host "[*] Verificando e instalando actualizaciones del sistema..." -ForegroundColor Cyan
pip install -r requirements.txt --quiet | Out-Null
Write-Host "[OK] Motor instalado y actualizado." -ForegroundColor Green

# 5. Ejecutar el orquestador principal
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan
Write-Host "[🚀] LANZANDO BOT..." -ForegroundColor Green
Write-Host "--------------------------------------------------------" -ForegroundColor Cyan

python main.py

# Si el bot se cierra o falla, pausar para leer el error
Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Proceso finalizado. Presiona ENTER para salir..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
