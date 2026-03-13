from src.scrapers.base_scraper import BaseScraper
from src.database import agregar_medio
from src.config import KEYWORDS_PRIORITY
import re

class SeriesBiblicasScraper(BaseScraper):
    """
    Scraper inteligente para seriesbiblicas.net.
    Ahora prioriza contenido temático y soporta múltiples fuentes.
    """
    
    def parse_movies(self):
        # Escaneamos tanto el Home como la sección de Películas para mayor frescura
        fuentes = [self.base_url, "https://seriesbiblicas.net/"]
        todas_encontradas = []

        for url in fuentes:
            print(f"  -> Escaneando fuente: {url}")
            soup = self.fetch_page(url)
            if not soup: continue
            todas_encontradas.extend(soup.find_all('a'))

        procesados = 0
        agregados = 0
        vistos = set()
        encontradas_prioridad = []
        encontradas_normales = []
        
        for a in todas_encontradas:
            href = a.get('href', '')
            if not href.startswith('https://seriesbiblicas.net/'): continue
            if href in vistos: continue
            vistos.add(href)
            
            titulo = a.get('title')
            if not titulo:
                img = a.find('img')
                if img: titulo = img.get('alt') or img.get('title')
            if not titulo: titulo = a.text.strip()

            if not titulo or len(titulo) < 3:
                if "seriesbiblicas.net/p" in href:
                    titulo = "Pelicula_" + href.strip('/').split('/')[-1]
                else: continue

            tipo = "pelicula" if "/p" in href else ("serie" if "/serie" in href or "temporada" in href else None)
            if not tipo: continue

            # Lógica de Prioridad: ¿Contiene alguna palabra de Semana Santa?
            es_prioridad = any(word.lower() in titulo.lower() for word in KEYWORDS_PRIORITY)
            
            peli_data = {"titulo": titulo, "url": href, "tipo": tipo}
            if es_prioridad:
                encontradas_prioridad.append(peli_data)
            else:
                encontradas_normales.append(peli_data)

        # Primero procesamos las de prioridad para que queden arriba en la cola
        print(f"  -> Encontradas: {len(encontradas_prioridad)} prioritarias, {len(encontradas_normales)} normales.")
        
        for peli in encontradas_prioridad + encontradas_normales:
            if agregados >= self.max_movies: break
            
            # Si el link es de seriesbiblicas, intentamos extraer el video real interno
            url_final = peli['url']
            if "seriesbiblicas.net/p" in url_final:
                video_real = self.extraer_video_interno(url_final)
                if video_real:
                    url_final = video_real

            fue_nueva = agregar_medio(peli['titulo'], url_final, peli['tipo'])
            if fue_nueva:
                agregados += 1
                print(f"  -> [NUEVO] {'🌟 ' if peli in encontradas_prioridad else ''}{peli['titulo']}")
        
        return []

    def extraer_video_interno(self, url_peli):
        """Entra en la peli y busca el iframe de ok.ru, vk.com, etc."""
        try:
            soup = self.fetch_page(url_peli)
            if not soup: return None
            
            # Buscar iframes comunes
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if any(x in src for x in ['ok.ru', 'vk.com', 'mail.ru', 'youtube.com']):
                    # Asegurar que el link sea absoluto
                    if src.startswith('//'):
                        src = 'https:' + src
                    return src
            
            # Buscar tags video (menos común pero posible)
            video = soup.find('video')
            if video:
                src = video.get('src')
                if src: return src

        except Exception as e:
            print(f"Error extrayendo video interno de {url_peli}: {e}")
        return None

