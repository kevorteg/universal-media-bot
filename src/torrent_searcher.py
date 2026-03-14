import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
import time

class TorrentHunter:
    """
    Motor de búsqueda de Magnets (El Cazador).
    Encuentra enlaces automáticos en trackers populares.
    """
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
        # Lista de espejos/trackers que el bot conoce
        self.mirrors = [
            "https://dontorrent.org",
            "https://elitetorrent.li",
            "https://vostit.com" # Fallback
        ]

    def buscar_en_dontorrent(self, titulo):
        """Busca específicamente en DonTorrent (Especialista en Castellano/Latino)"""
        try:
            # DonTorrent usa /buscar/{termino}
            query = urllib.parse.quote(titulo.replace(" ", "-"))
            for domain in ["https://dontorrent.org", "https://dontorrent.cc"]: # Probamos mirrors conocidos
                search_url = f"{domain}/buscar/{query}"
                print(f"      [Hunter] Husmeando en {domain}...")
                
                resp = requests.get(search_url, headers=self.headers, timeout=10)
                if resp.status_code != 200: continue
                
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Buscamos el primer resultado que sea película o serie
                items = soup.select('div.text-center a[href*="/pelicula/"], div.text-center a[href*="/serie/"]')
                
                for item in items:
                    link_detalle = domain + item['href']
                    # Entramos al detalle para sacar el magnet
                    print(f"      [Hunter] Posible presa encontrada: {item.text.strip()}")
                    
                    det_resp = requests.get(link_detalle, headers=self.headers, timeout=10)
                    if det_resp.status_code == 200:
                        det_soup = BeautifulSoup(det_resp.text, 'html.parser')
                        # El magnet suele estar en un botón data-href o en un script
                        magnet_link = det_soup.find('a', href=re.compile(r'^magnet:\?'))
                        if magnet_link:
                            return magnet_link['href']
            return None
        except Exception as e:
            print(f"      [!] Hunter Error (DonTorrent): {e}")
            return None

    def buscar_en_fallback(self, titulo):
        """Búsqueda de último recurso en agregadores globales"""
        try:
            # Usamos un agregador de magnets simple (limpio de JS pesado si es posible)
            # Nota: Esto es un ejemplo, se puede expandir a Jackett si el usuario es Pro
            query = urllib.parse.quote(f"{titulo} spanish magnet")
            search_url = f"https://www.google.com/search?q={query}" # Solo para ver si hay suerte en snippets
            # En una implementación real usamos APIs de búsqueda
            return None
        except:
            return None

    def extraer_magnet_de_pagina(self, url):
        """Entra a una web de torrents y busca el Magnet Link dentro"""
        try:
            print(f"      [Hunter] Extrayendo magnet de la página: {url}")
            resp = requests.get(url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Intentamos varios selectores comunes para magnets
                magnet = soup.find('a', href=re.compile(r'^magnet:\?'))
                if magnet:
                    return magnet['href']
                
                # Fallback: buscar en botones con onclick o data-href
                for tag in soup.find_all(['a', 'button'], attrs={"data-href": True}):
                    if "magnet:?" in tag['data-href']:
                        return tag['data-href']
            return None
        except Exception as e:
            print(f"      [!] Hunter Error al extraer de página: {e}")
            return None

    def buscar_en_btdig(self, titulo):
        """Búsqueda DHT en BTDigg (Muy estable para magnets globales)"""
        try:
            query = urllib.parse.quote(f"{titulo} spanish")
            search_url = f"https://www.btdig.com/search?q={query}"
            print(f"      [Hunter] Rastreando en DHT (BTDigg)...")
            
            resp = requests.get(search_url, headers=self.headers, timeout=10)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # BTDigg suele poner los magnets en la clase 'torrent_magnet'
                magnets = soup.select('div.one_result a[href^="magnet:?"]')
                if magnets:
                    # Retornamos el primero que suele ser el más relevante
                    return magnets[0]['href']
            return None
        except:
            return None

def buscar_magnet_en_google(titulo):
    """
    Función de búsqueda universal. 
    Llamada por el downloader cuando no hay un link directo.
    """
    hunter = TorrentHunter()
    
    # 1. Intentamos trackers especializados (DonTorrent, etc)
    magnet = hunter.buscar_en_dontorrent(titulo)
    if magnet: return magnet
    
    # 2. Intentamos buscador DHT global
    magnet = hunter.buscar_en_btdig(titulo)
    if magnet: return magnet

    print(f"    ❌ [HUNTER] La presa escapó. No se encontró magnet automático.")
    return None

def resolver_url_a_magnet(url):
    """
    Si el usuario pone una web de torrents, el Hunter va y saca el magnet.
    """
    if not url: return None
    if url.startswith("magnet:?"): return url
    
    # Si parece una URL de una web de torrents conocida
    trackers_conocidos = ["dontorrent", "elitetorrent", "vivatorrents", "mejortorrent", "divxtotal"]
    if any(tk in url.lower() for tk in trackers_conocidos):
        hunter = TorrentHunter()
        return hunter.extraer_magnet_de_pagina(url)
    
    return None
