import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env si existe
load_dotenv()

# Rutas principales del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carpeta de datos (SQLite)
DATA_DIR = os.path.join(BASE_DIR, "data")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

DB_PATH = os.path.join(DATA_DIR, "tracker.db")

# Configuración de descargas (Leyendo del .env con fallback)
DOWNLOADS_DIR = os.getenv("DOWNLOAD_DIR", r"D:\pelis cristianas")

if not os.path.exists(DOWNLOADS_DIR):
    try:
        os.makedirs(DOWNLOADS_DIR)
        print(f"Carpeta creada exitosamente: {DOWNLOADS_DIR}")
    except Exception as e:
        print(f"No se pudo crear la carpeta en {DOWNLOADS_DIR}, usando ruta local. Error: {e}")
        DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
        os.makedirs(DOWNLOADS_DIR, exist_ok=True)

# Límite de películas a descargar
MAX_MOVIES_TO_DOWNLOAD = int(os.getenv("MAX_MOVIES_TO_DOWNLOAD", 20))

# API Keys (Cargadas de manera segura)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

if not TMDB_API_KEY:
    print("[⚠] ADVERTENCIA: No se encontró TMDB_API_KEY en el archivo .env")

# Notificaciones Telegram (Opcionales)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# Priorización Inteligente (Semana Santa e Imprescindibles)
KEYWORDS_PRIORITY = [
    "Jesús", "Pasión", "Cristo", "Semana Santa", "Moisés", "Biblia", 
    "Resurrección", "Apocalipsis", "Noé", "Abraham", "Pedro", "Pablo",
    "Evangelio", "Vencedores", "Prueba de Fuego", "La Cabaña"
]

# qBittorrent Config
QB_BASE_URL = os.getenv("QB_URL", "http://127.0.0.1:8080")
QB_USERNAME = os.getenv("QB_USER", "admin")
QB_PASSWORD = os.getenv("QB_PASS", "adminadmin")

# Global Search Config
PREFERRED_LANG = os.getenv("PREFERRED_LANGUAGE", "es-MX")
PREFERRED_GENRE = os.getenv("PREFERRED_GENRE", "") # ID de genero de TMDB


