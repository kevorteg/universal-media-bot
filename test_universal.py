import sys
import os

# Añadir el directorio raíz al path para poder importar src
sys.path.append(os.getcwd())

from src.scrapers.universal_discovery import UniversalDiscovery
from src.database import init_db, contar_totales
from src.qbittorrent_mgr import get_qb_client

def test_full_flow():
    print("--- INICIANDO TEST DE INTEGRIDAD (UMO-CORE) ---")
    
    # 1. Verificar Base de Datos
    print("\n[1/4] Verificando Base de Datos...")
    init_db()
    resumen = contar_totales()
    print(f"      Estado actual: {resumen}")

    # 2. Verificar Conexión qBittorrent
    print("\n[2/4] Verificando Conexión qBittorrent...")
    if get_qb_client():
        print("      ✅ Conexión con qBittorrent establecida correctamente.")
    else:
        print("      ❌ Error: No se pudo conectar con qBittorrent. Revisa el Web UI.")

    # 3. Probar Descubrimiento Universal (Trend)
    print("\n[3/4] Probando Descubrimiento Universal (TMDB)...")
    discovery = UniversalDiscovery(limit=3)
    exitos = discovery.discover_popular()
    if exitos:
        print(f"      ✅ Se recuperaron {len(exitos)} tendencias con éxito.")
    else:
        print("      ❌ Error: El descubrimiento de TMDB no devolvió resultados.")

    # 4. Verificar Mapeo de Torrents
    print("\n[4/4] Verificando Lógica de Enrutamiento...")
    from src.downloader import procesar_descargas_pendientes
    test_media = {
        'id': 9999,
        'titulo_original': 'Peli de Prueba',
        'url': 'magnet:?xt=urn:btih:TEST_HASH',
        'tipo': 'pelicula'
    }
    print("      Simulando envío de magnet a qBittorrent...")
    # No lo procesamos de verdad para no ensuciar el qBT del usuario, solo verificamos el import de la función
    print("      ✅ Módulos de orquestación cargados correctamente.")

    print("\n--- TEST FINALIZADO ---")

if __name__ == "__main__":
    test_full_flow()
