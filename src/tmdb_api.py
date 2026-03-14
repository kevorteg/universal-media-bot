import requests
from src.config import TMDB_API_KEY, OMDB_API_KEY

def buscar_en_tmdb(titulo):
    """
    Busca una película en TMDB por título.
    Retorna un diccionario con: titulo_oficial, año, id_tmdb, poster_url
    """
    if not TMDB_API_KEY:
        print("[!] Advertencia: TMDB_API_KEY no configurado.")
        return None

    # Limpiar título para buscar mejor
    query = titulo.replace("_", " ").split('-')[0].strip()
    
    # Endpoint de búsqueda (multi para soportar pelis y series)
    url = f"https://api.themoviedb.org/3/search/multi"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "es-MX", # Latino por defecto (o es-ES)
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        
        # Filtramos para quedarnos solo con de tipo movie o tv
        results = [r for r in data.get("results", []) if r.get("media_type") in ("movie", "tv")]
        
        if len(results) > 0:
            # Tomamos el primer resultado
            item = results[0]
            
            titulo_oficial = item.get("title") or item.get("name") or item.get("original_title") or item.get("original_name")
            
            # Extraer solo el año
            fecha = item.get("release_date") or item.get("first_air_date")
            anio = None
            if fecha:
                anio = int(fecha.split("-")[0])
                
            poster_url = None
            if item.get("poster_path"):
                poster_url = f"https://image.tmdb.org/t/p/w500{item['poster_path']}"
                
            return {
                "titulo_limpio": titulo_oficial,
                "anio": anio,
                "tmdb_id": item.get("id"),
                "poster_url": poster_url,
                "media_type": item.get("media_type")
            }
        else:
            return None
            
    except Exception as e:
        print(f"[TMDB] Error buscando '{titulo}': {e}")
        return None

def descargar_poster(url_poster, ruta_destino):
    """Descarga el poster de TMDB a la ruta local especificada."""
    if not url_poster:
        return False
        
    try:
        res = requests.get(url_poster)
        res.raise_for_status()
        with open(ruta_destino, 'wb') as f:
            f.write(res.content)
        return True
    except Exception as e:
        print(f"[POSTER] Error descargando poster desde {url_poster}: {e}")
        return False
