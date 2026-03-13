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
    
    # Endpoint de búsqueda
    url = f"https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": query,
        "language": "es-ES", # Buscar en español
    }

    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        
        if data.get("results") and len(data["results"]) > 0:
            # Tomamos el primer resultado
            peli = data["results"][0]
            
            titulo_oficial = peli.get("title") or peli.get("original_title")
            # Extraer solo el año de release_date "2014-03-21"
            anio = None
            if peli.get("release_date"):
                anio = int(peli["release_date"].split("-")[0])
                
            poster_url = None
            if peli.get("poster_path"):
                poster_url = f"https://image.tmdb.org/t/p/w500{peli['poster_path']}"
                
            return {
                "titulo_limpio": titulo_oficial,
                "anio": anio,
                "tmdb_id": peli.get("id"),
                "poster_url": poster_url
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
