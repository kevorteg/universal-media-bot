import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from src.config import DOWNLOADS_DIR
from src.database import actualizar_estado
from src.tmdb_api import descargar_poster
from src.utils import sanitize_filename
from src.notifier import send_telegram_message
from src.qbittorrent_mgr import enviar_a_qbittorrent

def descargar_pelicula(media_db):
    """
    Descarga una película usando yt-dlp.
    Crea una subcarpeta con el nombre oficial + año.
    Descarga el póster si existe.
    """
    # Preferimos el nombre de TMDB si lo tenemos
    titulo_base = media_db.get("titulo_limpio") or media_db.get("titulo_original")
    
    # Construir el nombre de la carpeta: Ej "Dios no esta muerto (2014)"
    nombre_carpeta = sanitize_filename(titulo_base)
    if media_db.get("anio"):
        nombre_carpeta += f" ({media_db['anio']})"
        
    # Crear ruta de descarga final
    carpeta_destino = os.path.join(DOWNLOADS_DIR, nombre_carpeta)
    os.makedirs(carpeta_destino, exist_ok=True)
    
    # Archivo mp4
    output_path = os.path.join(carpeta_destino, f"{nombre_carpeta}.mp4")

    print(f"\n[INICIANDO] Descarga: {nombre_carpeta}")
    print(f"URL: {media_db['url']}")
    print(f"Carpeta: {carpeta_destino}")
    
    # Descargar póster en paralelo/antes si existe
    if media_db.get("poster_url"):
        poster_path = os.path.join(carpeta_destino, "poster.jpg")
        print("  -> Descargando Póster...")
        descargar_poster(media_db["poster_url"], poster_path)

    # Marcamos en la BD que la descarga ha comenzado
    actualizar_estado(media_db['id'], "descargando")
    send_telegram_message(f"⏳ <b>Iniciando proceso:</b>\n{titulo_base}")

    # --- LÓGICA DE CAZADOR (HUNTER) ---
    url_final = media_db['url']
    
    # Si es una URL de tracker (DonTorrent, etc), la resolvemos a Magnet
    from src.torrent_searcher import resolver_url_a_magnet, buscar_magnet_en_google
    resolved_magnet = resolver_url_a_magnet(url_final)
    if resolved_magnet:
        url_final = resolved_magnet
    
    # Si sigue siendo un comando de búsqueda automática
    if url_final.startswith("torrent:"):
        print(f"  -> [HUNTER] Iniciando cacería automática para: {media_db['titulo_original']}")
        magnet = buscar_magnet_en_google(media_db['titulo_original'])
        if magnet:
            url_final = magnet
        else:
            print(f"  [!] La presa escapó. No se encontró torrent automático.")
            actualizar_estado(media_db['id'], "error", mensaje_error="No encontrado")
            return False

    if url_final.startswith("magnet:?") or ".torrent" in url_final.lower():
        print(f"  -> Enviando a qBittorrent...")
        exito = enviar_a_qbittorrent(url_final, nombre_carpeta)
        if exito:
            actualizar_estado(media_db['id'], "completada", mensaje_error="En qBittorrent")
            send_telegram_message(f"🏴‍☠️ <b>Tracker/Magnet Capturado:</b>\n{titulo_base}")
            return True
        else:
            actualizar_estado(media_db['id'], "error", mensaje_error="Error qBT")
            return False

    # RESOLUCIÓN EN CALIENTE: Si la URL es de la web...
    url_descarga = url_final
    if "seriesbiblicas.net" in url_descarga:
        print("  -> Link de web detectado. Buscando video interno...")
        from src.scrapers.seriesbiblicas import SeriesBiblicasScraper
        temp_scraper = SeriesBiblicasScraper(base_url="", max_movies=1)
        video_real = temp_scraper.extraer_video_interno(url_descarga)
        if video_real:
            url_descarga = video_real
            print(f"  -> Link resuelto: {url_descarga}")
        else:
            print("  [!] No se pudo resolver el video interno. Intentando con la URL original...")

    try:
        # Ejecutar yt-dlp usando subprocess
        comando = [
            "yt-dlp",
            "-f", "bestvideo+bestaudio/best",
            "--merge-output-format", "mp4",
            "--embed-thumbnail",
            "--add-metadata",
            # Quitamos --javascript-location node si da problemas, yt-dlp suele detectarlo solo si está en el PATH
            "-o", output_path,
            "--no-playlist"
        ]
        
        comando.append(url_descarga)
        
        # Ejecutamos viendo la salida en consola para diagnosticar
        result = subprocess.run(
            comando, 
            check=True, 
            timeout=10800
        )
        
        print(f"[ÉXITO] Archivo guardado en: {output_path}")
        # Actualizar estado e inyectar la ruta_carpeta base
        actualizar_estado(media_db['id'], "completada", ruta_carpeta=carpeta_destino)
        send_telegram_message(f"✅ <b>Descarga Completada:</b>\n{titulo_base} (Guardado en D:)")
        return True

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr[:200] if e.stderr else "Error desconocido de yt-dlp"
        print(f"[ERROR] Falló la descarga de {titulo_base}:")
        print(error_msg)
        actualizar_estado(media_db['id'], "error", mensaje_error=error_msg)
        send_telegram_message(f"❌ <b>Error de Descarga:</b>\n{titulo_base}\n<i>Motivo:</i> {str(e)}")
        return False
        
    except Exception as e:
        error_msg = str(e)[:200]
        print(f"[ERROR GENERAL]: {error_msg}")
        actualizar_estado(media_db['id'], "error", mensaje_error=error_msg)
        send_telegram_message(f"🚨 <b>Error General:</b>\n{titulo_base}\n<i>Log:</i> {error_msg}")
        return False

def procesar_descargas_pendientes(pendientes):
    """Descarga de películas con cola y concurrencia máxima de 3 workers."""
    total = len(pendientes)
    print(f"\n--- Iniciando Cola de Descargas ({total} pendientes) ---")
    send_telegram_message(f"🚀 Iniciando orquestador: <b>{total} películas en cola</b>.")
    
    exitosas = 0
    fallidas = 0
    
    # max_workers define el limite de peliculas corriendo en simultáneo
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Iniciamos todas las tareas
        futuros = {executor.submit(descargar_pelicula, peli): peli for peli in pendientes}
        
        for idx, futuro in enumerate(as_completed(futuros), 1):
            peli = futuros[futuro]
            nombre = peli.get("titulo_limpio") or peli.get("titulo_original")
            try:
                exito = futuro.result()
                if exito:
                    exitosas += 1
                else:
                    fallidas += 1
                print(f"--- [{idx}/{total}] Hilo de {nombre} Terminado ---")
            except Exception as exc:
                print(f"La tarea de {nombre} arrojó una excepción: {exc}")
                fallidas += 1
                
    resumen = f"🏁 <b>Cola Finalizada</b>\nÉxito: {exitosas} | Errores: {fallidas}"
    print(f"\n--- {resumen} ---")
    send_telegram_message(resumen)

