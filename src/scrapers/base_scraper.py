import time
import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod

class BaseScraper(ABC):
    """
    Clase base abstracta para todos los scrapers de películas.
    Garantiza que todos los nuevos scrapers implementen la misma interfaz.
    """
    
    def __init__(self, base_url, max_movies=20):
        self.base_url = base_url
        self.max_movies = max_movies
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    def fetch_page(self, url):
        """Metodo comun para descargar una pagina y convertirla a BeautifulSoup."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"[ERROR de RED] en {url}: {e}")
            return None

    @abstractmethod
    def parse_movies(self) -> list:
        """
        Debe ser implementado por cada sitio web particular.
        Debe retornar una lista de diccionarios:
        [{'titulo': 'La Cabaña', 'url': 'http...', 'tipo': 'pelicula'}, ...]
        """
        pass

    def run(self):
        """Método principal de orquestación del scraper."""
        print(f"\n[{self.__class__.__name__}] Iniciando scrapeo en: {self.base_url}")
        
        movies = self.parse_movies()
        
        if not movies:
            print(f"[{self.__class__.__name__}] No se encontraron películas.")
            return []
            
        print(f"[{self.__class__.__name__}] Scrapeo finalizado. {len(movies)} elementos encontrados.")
        return movies
