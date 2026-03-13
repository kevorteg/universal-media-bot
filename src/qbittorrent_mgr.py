import qbittorrentapi
from src.config import QB_BASE_URL, QB_USERNAME, QB_PASSWORD, DOWNLOADS_DIR
import os

def get_qb_client():
    """Inicia sesión y devuelve el cliente de qBittorrent."""
    try:
        qbt_client = qbittorrentapi.Client(
            host=QB_BASE_URL,
            username=QB_USERNAME,
            password=QB_PASSWORD,
        )
        qbt_client.auth_log_in()
        return qbt_client
    except Exception as e:
        print(f"[!] Error conectando a qBittorrent: {e}")
        return None

def enviar_a_qbittorrent(magnet_link, nombre_peli):
    """Envía un enlace magnet o archivo torrent a qBittorrent."""
    qbt = get_qb_client()
    if not qbt:
        return False
        
    try:
        # Definir la subcarpeta para la película
        save_path = os.path.join(DOWNLOADS_DIR, nombre_peli)
        os.makedirs(save_path, exist_ok=True)
        
        qbt.torrents_add(
            urls=magnet_link,
            save_path=save_path,
            rename=nombre_peli
        )
        print(f"  -> [OK] Enviado a qBittorrent: {nombre_peli}")
        return True
    except Exception as e:
        print(f"  -> [!] Falló al agregar torrent a qBittorrent: {e}")
        return False

def obtener_progreso_torrents():
    """Devuelve un diccionario con el progreso de los torrents activos."""
    qbt = get_qb_client()
    if not qbt:
        return {}
        
    try:
        torrents = qbt.torrents_info()
        return {t.name: {"progress": round(t.progress * 100, 1), "state": t.state} for t in torrents}
    except:
        return {}
