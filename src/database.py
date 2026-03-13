import sqlite3
import os
import threading
from datetime import datetime
from src.config import DB_PATH
from src.tmdb_api import buscar_en_tmdb

# Lock global para evitar concurrencia en SQLite que cause 'database is locked'
db_lock = threading.Lock()

def get_connection():
    """Devuelve una conexión a la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa la estructura de la base de datos con soporte para TMDB."""
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS multimedia (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo_original TEXT NOT NULL,
                titulo_limpio TEXT,
                anio INTEGER,
                tmdb_id INTEGER,
                poster_url TEXT,
                url TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                ruta_carpeta TEXT,
                fecha_agregado TEXT,
                fecha_descarga TEXT
            )
        """)
        conn.commit()
    print("Base de datos de medios inicializada correctamente.")

def agregar_medio(titulo, url, tipo):
    """Agrega un nuevo medio y enriquece sus datos con TMDB si es posible."""
    insertado = False
    try:
        # Enriquecer con TMDB
        datos_tmdb = buscar_en_tmdb(titulo)
        
        titulo_limpio = None
        anio = None
        tmdb_id = None
        poster_url = None
        
        if datos_tmdb:
            titulo_limpio = datos_tmdb["titulo_limpio"]
            anio = datos_tmdb["anio"]
            tmdb_id = datos_tmdb["tmdb_id"]
            poster_url = datos_tmdb["poster_url"]
            print(f"  -> TMDB Match: {titulo_limpio} ({anio})")

        fecha_agregado = datetime.now().isoformat()
        
        with db_lock:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO multimedia (titulo_original, titulo_limpio, anio, tmdb_id, poster_url, url, tipo, fecha_agregado) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (titulo, titulo_limpio, anio, tmdb_id, poster_url, url, tipo, fecha_agregado))
            conn.commit()
            insertado = True
            
    except sqlite3.IntegrityError:
        # Duplicado
        pass
    except Exception as e:
        print(f"Error insertando en base de datos: {e}")
        
    return insertado

def obtener_pendientes(tipo="pelicula", limite=None):
    """Obtiene pendientes filtrando por tipo (por defecto, peliculas)."""
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
        query = "SELECT * FROM multimedia WHERE estado = 'pendiente' AND tipo = ?"
        parametros = [tipo]
        
        if limite:
            query += " LIMIT ?"
            parametros.append(limite)
            
        cursor.execute(query, parametros)
        resultados = [dict(row) for row in cursor.fetchall()]
        
    return resultados

def actualizar_estado(id_medio, estado, ruta_carpeta=None, mensaje_error=None):
    """Actualiza el estado de la descarga guardando la carpeta principal."""
    fecha_actual = datetime.now().isoformat()
    
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
        if estado == 'completada':
            cursor.execute("""
                UPDATE multimedia 
                SET estado = ?, ruta_carpeta = ?, fecha_descarga = ?
                WHERE id = ?
            """, (estado, ruta_carpeta, fecha_actual, id_medio))
        else:
            estado_con_error = f"error: {mensaje_error}" if mensaje_error else "error"
            cursor.execute("""
                UPDATE multimedia 
                SET estado = ?, fecha_descarga = ?
                WHERE id = ?
            """, (estado_con_error, fecha_actual, id_medio))
            
        conn.commit()

def contar_totales():
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
        cursor.execute("SELECT estado, COUNT(*) as cantidad FROM multimedia GROUP BY estado")
        resultados = {row['estado']: row['cantidad'] for row in cursor.fetchall()}
    return resultados

def obtener_todos():
    """Obtiene todos los medios para el panel web."""
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
        cursor.execute("SELECT * FROM multimedia ORDER BY fecha_agregado DESC")
        resultados = [dict(row) for row in cursor.fetchall()]
    return resultados

def obtener_por_id(id_medio):
    """Consulta una entrada específica por su ID."""
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM multimedia WHERE id = ?", (id_medio,))
            row = cursor.fetchone()
    return dict(row) if row else None

def eliminar_errores():
    """Elimina permanentemente de la BD todas las descargas marcadas con error."""
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM multimedia WHERE estado LIKE 'error%'")
            eliminados = cursor.rowcount
            conn.commit()
    return eliminados

def actualizar_metadatos(id_medio, titulo, anio):
    """Fuerza un título local, año, y devuelve el estado a 'pendiente' para reintento."""
    with db_lock:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE multimedia 
                SET titulo_limpio = ?, anio = ?, estado = 'pendiente', fecha_descarga = NULL
                WHERE id = ?
            """, (titulo, anio, id_medio))
            conn.commit()

# Inicializar DB siempre al importar
init_db()
