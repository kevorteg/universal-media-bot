import requests
from src.config import TMDB_API_KEY, PREFERRED_LANG, PREFERRED_GENRE
from src.database import agregar_medio

class UniversalDiscovery:
    def __init__(self, limit=20):
        self.limit = limit

    def discover_popular(self):
        """Descubre películas populares usando la API de TMDB."""
        print(f"🔍 Descubriendo películas populares ({PREFERRED_LANG})...")
        
        endpoint = "https://api.themoviedb.org/3/discover/movie"
        params = {
            "api_key": TMDB_API_KEY,
            "language": PREFERRED_LANG,
            "sort_by": "popularity.desc",
            "include_adult": "false",
            "page": 1
        }
        
        if PREFERRED_GENRE:
            params["with_genres"] = PREFERRED_GENRE

        try:
            response = requests.get(endpoint, params=params)
            if response.status_code != 200:
                print(f"[!] Error TMDB: {response.status_code}")
                return []
                
            resultados = response.json().get('results', [])
            agregados = 0
            
            for movie in resultados:
                if agregados >= self.limit: break
                
                titulo = movie.get('title')
                anio = movie.get('release_date', '')[:4]
                # Para descubrimiento universal, la URL inicial es una búsqueda por torrent
                url_busqueda = f"torrent:{titulo} {anio} latino spanish"
                
                # Intentamos agregar a la BD como pendiente
                if agregar_medio(titulo, url_busqueda, "pelicula"):
                    agregados += 1
                    print(f"  -> [NUEVO] {titulo} ({anio})")
                    
            print(f"✅ Se descubrieron {agregados} nuevas películas.")
            return resultados
            
        except Exception as e:
            print(f"[!] Error en descubrimiento universal: {e}")
            return []
