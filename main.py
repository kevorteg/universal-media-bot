import sys
import os
import time
from src.database import obtener_pendientes, contar_totales, agregar_medio
from src.scrapers.seriesbiblicas import SeriesBiblicasScraper
from src.downloader import procesar_descargas_pendientes
from src.config import DOWNLOADS_DIR, BASE_DIR, MAX_MOVIES_TO_DOWNLOAD
from src.web_admin import run_server
from apscheduler.schedulers.blocking import BlockingScheduler

def print_resumen():
    print("\n================== RESUMEN DE ESTADO ==================")
    totales = contar_totales()
    print(f"Carpeta Destino: {DOWNLOADS_DIR}")
    for estado, cantidad in totales.items():
        print(f" - {estado.capitalize()}: {cantidad}")
    print("=======================================================\n")

def importar_desde_txt():
    ruta = os.path.join(BASE_DIR, "peliculas.txt")
    if not os.path.exists(ruta):
        print(f"[!] No se encontró el archivo {ruta}. Créalo y pon un nombre por línea.")
        return
        
    print(f"Leyendo desde {ruta}...")
    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.readlines()
        
    agregados = 0
    import re
    
    for linea in lineas:
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue
            
        # Buscar si hay una URL explícita en la línea
        match_url = re.search(r'(https?://[^\s()]+)', linea_limpia)
        if match_url:
            url_real = match_url.group(1)
            titulo = linea_limpia.split('http')[0].strip(' :') or "Desconocido"
            
            # Si el link es de seriesbiblicas, intentamos extraer el video real interno de inmediato
            if "seriesbiblicas.net/p" in url_real:
                from src.scrapers.seriesbiblicas import SeriesBiblicasScraper
                scraper_temp = SeriesBiblicasScraper(base_url="", max_movies=1)
                video_real = scraper_temp.extraer_video_interno(url_real)
                if video_real:
                    url_final = video_real
                else:
                    url_final = url_real
            else:
                url_final = url_real
        else:
            titulo = linea_limpia
            url_final = f"ytsearch:{titulo} pelicula cristiana completa en español"
            
        if agregar_medio(titulo, url_final, "pelicula"):
            agregados += 1
            
    print(f"\nSe importaron {agregados} películas desde el TXT hacia la Base de Datos.")

def limpiar_txt_completadas():
    """Remueve del peliculas.txt aquellas que ya se descargaron con éxito."""
    ruta = os.path.join(BASE_DIR, "peliculas.txt")
    if not os.path.exists(ruta): return

    from src.database import obtener_todos
    completadas = [p['titulo_original'].lower() for p in obtener_todos() if p['estado'] == 'completada']
    completadas_url = [p['url'].lower() for p in obtener_todos() if p['estado'] == 'completada']

    with open(ruta, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    nuevas_lineas = []
    borrados = 0
    for l in lineas:
        l_trim = l.strip().lower()
        if not l_trim: 
            nuevas_lineas.append(l)
            continue
            
        # Si el titulo o la url de la linea estan en completadas, la saltamos
        match = any(c in l_trim for c in completadas) or any(u in l_trim for u in completadas_url)
        if match:
            borrados += 1
        else:
            nuevas_lineas.append(l)

    with open(ruta, "w", encoding="utf-8") as f:
        f.writelines(nuevas_lineas)
    
    print(f"🧹 Limpieza completada: Se eliminaron {borrados} películas ya descargadas del archivo.")


def tarea_programada():
    """Rutina que ejecuta el demonio periódicamente."""
    print(f"\n[{time.strftime('%Y-%m-%d %H:%M:%S')}] ⚙ Iniciando rutina de Autopiloto...")
    
    # 1. Buscar nuevas pelis (Prioriza Semana Santa ahora)
    try:
        scraper = SeriesBiblicasScraper(
            base_url="https://seriesbiblicas.net/peliculas/",
            max_movies=MAX_MOVIES_TO_DOWNLOAD
        )
        print("[*] Escaneando web por contenido nuevo y temático...")
        scraper.run()
    except Exception as e:
        print(f"Error en Auto-Scraper: {e}")

    # 2. Descargar si hay pendientes
    pendientes = obtener_pendientes()
    if pendientes:
        print(f"[*] Se encontraron {len(pendientes)} películas listas para bajar.")
        procesar_descargas_pendientes(pendientes)
    else:
        print("[-] Todo al día. No se hallaron películas nuevas en esta ronda.")

def iniciar_demonio():
    """Bloquea el hilo principal y ejecuta tareas periódicas."""
    print("\n==================================================")
    print("🤖 MODO AUTOPILOTO (DEMONIO) ACTIVADO")
    print("El bot buscará y descargará películas nuevas cada 6 horas.")
    print("Presiona Ctrl+C para detener y volver al menú.")
    print("==================================================\n")
    
    # Ejecutamos la primera ronda de inmediato
    tarea_programada()
    
    scheduler = BlockingScheduler()
    scheduler.add_job(tarea_programada, 'interval', hours=6)
    try:
        scheduler.start()
    except KeyboardInterrupt:
        print("\n[!] Modo Autopiloto apagado. Volviendo al menú...")

def menu_principal():
    print("""
    --------------------------------------------------------
    BOT DE MEDIOS UNIVERSAL (Open Source Edition)
    --------------------------------------------------------
    [1] Arrancar Panel Web (Dashboard Interactivo)
    [2] Descubrir Tendencias (Búsqueda Universal TMDB)
    [3] Importar desde 'peliculas.txt' (Nombres o Magnets)
    [4] Iniciar Cola de Descarga (yt-dlp + Torrents)
    [5] Mostrar Estado BD
    [6] Limpiar 'peliculas.txt' (Borrar ya descargadas)
    [7] Buscar Torrent por Nombre (qBittorrent)
    [8] Arrancar en MODO AUTOPILOTO (Demonio 6H)
    [9] Salir
    """)
    return input("Elige una opción: ")

def main():
    while True:
        try:
            opcion = menu_principal()
            
            if opcion == '1':
                run_server()
            elif opcion == '2':
                from src.scrapers.universal_discovery import UniversalDiscovery
                discovery = UniversalDiscovery(limit=MAX_MOVIES_TO_DOWNLOAD)
                discovery.discover_popular()
            elif opcion == '3':
                importar_desde_txt()
            elif opcion == '4':
                try:
                    pendientes = obtener_pendientes()
                    if not pendientes:
                        print("¡No hay películas pendientes!")
                    else:
                        procesar_descargas_pendientes(pendientes)
                except KeyboardInterrupt:
                    print("\n[!] Proceso interrumpido por el usuario.")
            elif opcion == '5':
                print_resumen()
            elif opcion == '6':
                limpiar_txt_completadas()
            elif opcion == '7':
                nombre = input("Dime el nombre de la peli a buscar: ")
                print(f"Buscando magnet para '{nombre}'...")
                from src.torrent_searcher import buscar_magnet_en_google
                magnet = buscar_magnet_en_google(nombre)
                if magnet:
                    from src.qbittorrent_mgr import enviar_a_qbittorrent
                    enviar_a_qbittorrent(magnet, nombre)
                else:
                    print("No se encontró un magnet directo. Intenta buscarlo manualmente y pegarlo como URL.")
            elif opcion == '8':
                iniciar_demonio()
            elif opcion == '9':
                print("¡Hasta luego!")
                sys.exit(0)
            else:
                print("Opción no válida. Intenta de nuevo.")
                
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n¡Adiós!")
            sys.exit(0)

if __name__ == "__main__":
    main()

