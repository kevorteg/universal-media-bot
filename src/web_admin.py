from flask import Flask, render_template_string, jsonify, request, send_file, Response
import threading
import os
from src.database import obtener_todos, obtener_pendientes, eliminar_errores, actualizar_metadatos, obtener_por_id, eliminar_medio
from src.downloader import procesar_descargas_pendientes
from src.qbittorrent_mgr import obtener_progreso_torrents

app = Flask(__name__)

# Variable global para evitar descargas concurrentes
descargando = False

# HTML Embebido extendido con Modales, Filtros, Grid/Lista y Glassmorphism
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Universal Media Bot - Admin Premium</title>
    <!-- FontAwesome para iconos -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root { --primary: #007aff; --secondary: #34c759; --danger: #ff3b30; --dark: #1c1c1e; --bg: #f2f2f7; --card-bg: rgba(255, 255, 255, 0.75); }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg); margin: 0; padding: 20px; color: var(--dark); }
        
        /* Glassmorphism Header */
        .header { display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; background: rgba(255, 255, 255, 0.65); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); padding: 20px 30px; border-radius: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.05); margin-bottom: 30px; border: 1px solid rgba(255, 255, 255, 0.5); }
        h1 { margin: 0; font-size: 26px; font-weight: 700; background: -webkit-linear-gradient(45deg, var(--primary), #5ac8fa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        .toolbar { display: flex; gap: 15px; margin-top: 15px; width: 100%; justify-content: space-between; align-items: center; }
        .filters { display: flex; gap: 10px; }
        .view-toggles { display: flex; gap: 10px; }
        
        /* Botones estilo Apple */
        .btn { border: none; padding: 10px 20px; border-radius: 12px; cursor: pointer; font-weight: 600; font-size: 14px; transition: all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1); display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
        .btn-start { background: linear-gradient(135deg, var(--secondary), #28a745); color: white; }
        .btn-purge { background: linear-gradient(135deg, var(--danger), #c0392b); color: white; }
        .btn-edit { background: rgba(255, 255, 255, 0.8); color: var(--dark); padding: 8px 12px; border: 1px solid rgba(0,0,0,0.1); }
        .btn-play { background: linear-gradient(135deg, var(--primary), #0056b3); color: white; margin-top: 10px; width: 100%; justify-content: center; }
        .btn-del { background: rgba(255, 59, 48, 0.1); color: var(--danger); padding: 8px 12px; }
        .btn-del:hover { background: var(--danger); color: white; }
        .btn:hover { transform: scale(1.03); box-shadow: 0 7px 14px rgba(0,0,0,0.1); }
        .btn:active { transform: scale(0.97); }

        .filter-btn { background: rgba(255,255,255,0.7); border: 1px solid rgba(0,0,0,0.05); border-radius: 10px; padding: 8px 15px; cursor: pointer; font-weight: 500; color: #666; transition: 0.3s; }
        .filter-btn.active { background: var(--primary); color: white; border-color: var(--primary); box-shadow: 0 4px 10px rgba(0, 122, 255, 0.3); }

        /* Vistas (Cuadrícula / Lista) */
        .media-container { transition: all 0.4s ease; }
        
        /* Vista Cuadrícula (Grid) */
        .media-container.view-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 25px; }
        .view-grid .card { flex-direction: column; background: var(--card-bg); backdrop-filter: blur(10px); border-radius: 20px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.08); transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275); position: relative; border: 1px solid rgba(255,255,255,0.6); }
        .view-grid .card:hover { transform: translateY(-8px); box-shadow: 0 15px 35px rgba(0,0,0,0.15); }
        .view-grid .card img { width: 100%; height: 350px; object-fit: cover; background: #ddd; }
        .view-grid .card-body { padding: 20px; display: flex; flex-direction: column; }
        
        /* Vista Lista (List) */
        .media-container.view-list { display: flex; flex-direction: column; gap: 15px; }
        .view-list .card { display: flex; flex-direction: row; background: var(--card-bg); backdrop-filter: blur(10px); border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); align-items: center; padding: 10px; border: 1px solid rgba(255,255,255,0.6); }
        .view-list .card img { width: 80px; height: 120px; object-fit: cover; border-radius: 10px; }
        .view-list .card-body { padding: 0 20px; flex: 1; display: flex; flex-direction: column; justify-content: center; }
        .view-list .card-actions { display: flex; flex-direction: column; gap: 8px; padding-right: 15px; min-width: 150px; }
        .view-list .badge { position: relative; top: 0; right: 0; display: inline-block; margin-bottom: 5px; width: max-content; }

        .title { font-weight: 700; font-size: 16px; color: var(--dark); margin-bottom: 6px; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; }
        .info { font-size: 13px; color: #8e8e93; font-weight: 500; margin-bottom: 15px; }
        
        .badge { position: absolute; top: 15px; right: 15px; padding: 5px 12px; border-radius: 20px; font-size: 11px; font-weight: 800; color: white; z-index: 10; letter-spacing: 0.5px; text-transform: uppercase; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
        .badge-pendiente { background: linear-gradient(135deg, #ff9500, #ffcc00); }
        .badge-completada { background: linear-gradient(135deg, #34c759, #30b04c); }
        .badge-error { background: linear-gradient(135deg, #ff3b30, #ff2d55); }
        .badge-descargando { background: linear-gradient(135deg, #007aff, #5ac8fa); animation: pulse 2s infinite; }
        
        .card-buttons { display: flex; gap: 8px; margin-top: auto; }
        .view-list .card-buttons { display: none; } /* Ocultar botones grid en modo lista */

        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.6; } 100% { opacity: 1; } }
        
        /* Modales (Glass) */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.4); backdrop-filter: blur(5px); align-items: center; justify-content: center; }
        .modal-content { background: rgba(255,255,255,0.9); backdrop-filter: blur(20px); padding: 30px; border-radius: 24px; width: 90%; max-width: 500px; position: relative; box-shadow: 0 25px 50px rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.5); }
        .video-content { max-width: 900px; padding: 15px; background: rgba(0,0,0,0.8); }
        .close { position: absolute; top: 15px; right: 25px; font-size: 28px; font-weight: bold; cursor: pointer; color: #8e8e93; transition: 0.2s; }
        .close:hover { color: var(--danger); }
        input { width: 100%; padding: 12px 15px; margin: 10px 0 20px 0; border: 1px solid rgba(0,0,0,0.1); border-radius: 12px; box-sizing: border-box; background: rgba(255,255,255,0.8); font-size: 15px; transition: border-color 0.3s; }
        input:focus { outline: none; border-color: var(--primary); box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2); }
        label { font-weight: 600; font-size: 14px; color: #555; }
    </style>
</head>
<body>

<div class="header">
    <div style="display: flex; justify-content: space-between; width: 100%; align-items: center;">
        <h1><i class="fa-solid fa-play-circle" style="color:var(--primary)"></i> Universal Media Dashboard</h1>
        <div class="controls">
            <button class="btn btn-purge" onclick="purgarErrores()"><i class="fa-solid fa-trash"></i> Limpiar Errores</button>
            <button class="btn btn-purge" onclick="borrarTodoBD()"><i class="fa-solid fa-skull"></i> Borrar BD</button>
            <button class="btn btn-start" onclick="iniciarDescargas(this)"><i class="fa-solid fa-rocket"></i> Iniciar Descargas</button>
        </div>
    </div>
    
    <div class="toolbar">
        <div class="filters">
            <button class="filter-btn active" onclick="filterCards('all', this)"><i class="fa-solid fa-border-all"></i> Todos</button>
            <button class="filter-btn" onclick="filterCards('pelicula', this)"><i class="fa-solid fa-film"></i> Películas</button>
            <button class="filter-btn" onclick="filterCards('serie', this)"><i class="fa-solid fa-tv"></i> Series</button>
            <button class="filter-btn" onclick="filterCards('pendiente', this)"><i class="fa-solid fa-clock"></i> Pendientes</button>
            <button class="filter-btn" onclick="filterCards('completada', this)"><i class="fa-solid fa-check"></i> Completadas</button>
        </div>
        <div class="view-toggles">
            <button class="filter-btn active" id="btn-grid" onclick="setView('grid')"><i class="fa-solid fa-grip"></i> Grid</button>
            <button class="filter-btn" id="btn-list" onclick="setView('list')"><i class="fa-solid fa-list"></i> Lista</button>
        </div>
    </div>
</div>

<div class="media-container view-grid" id="main-container">
    {% for p in peliculas %}
    {% set status_class = 'completada' if p.estado == 'completada' else ('error' if 'error' in p.estado else ('descargando' if p.estado == 'descargando' else 'pendiente')) %}
    
    <div class="card item-card" data-tipo="{{ p.tipo.lower() if p.tipo else 'pelicula' }}" data-estado="{{ status_class }}">
        <span class="badge badge-{{ status_class }}">
            {{ status_class|upper }}
        </span>
        <img src="{{ p.poster_url if p.poster_url else 'https://via.placeholder.com/250x350?text=Poster+No+Encontrado' }}" alt="Poster" loading="lazy">
        
        <!-- Para vista Grid -->
        <div class="card-body">
            <span class="title" title="{{ p.titulo_limpio or p.titulo_original }}">{{ p.titulo_limpio or p.titulo_original }}</span>
            <div class="info"><i class="fa-regular fa-calendar"></i> {{ p.anio or 'S/A' }} &nbsp;|&nbsp; <i class="fa-solid {{ 'fa-tv' if 'serie' in p.tipo|lower else 'fa-film' }}"></i> {{ p.tipo|capitalize }}</div>
            
            {% if p.id|string in torrents_info %}
                <div style="background:rgba(0,0,0,0.05); height:8px; border-radius:4px; margin:8px 0; overflow:hidden;">
                    <div style="background:var(--primary); height:100%; width:{{ torrents_info[p.id|string].progress }}%; border-radius:4px;"></div>
                </div>
                <div style="font-size:11px; font-weight:600; color:var(--primary); margin-bottom:10px;">
                     <i class="fa-brands fa-hubspot"></i> qBT: {{ torrents_info[p.id|string].progress }}% ({{ torrents_info[p.id|string].state }})
                </div>
            {% endif %}

            <div class="card-buttons">
                {% if status_class == 'completada' %}
                    <button class="btn btn-play" onclick='verVideo({{ p.id }}, {{ (p.titulo_limpio or p.titulo_original) | tojson }})'><i class="fa-solid fa-play"></i> Previa</button>
                {% else %}
                    <button class="btn btn-edit" style="flex:1" onclick='abrirEditor({{ p.id }}, {{ (p.titulo_limpio or p.titulo_original) | tojson }}, {{ (p.anio or "") | tojson }}, {{ (p.url or "") | tojson }})'><i class="fa-solid fa-pen"></i></button>
                {% endif %}
                <button class="btn btn-del" onclick="borrarMedio({{ p.id }})"><i class="fa-solid fa-trash"></i></button>
            </div>
        </div>

        <!-- Para vista List -->
        <div class="card-actions">
            {% if status_class == 'completada' %}
                <button class="btn btn-play" onclick='verVideo({{ p.id }}, {{ (p.titulo_limpio or p.titulo_original) | tojson }})'><i class="fa-solid fa-play"></i> Ver Previa</button>
            {% else %}
                <button class="btn btn-edit" onclick='abrirEditor({{ p.id }}, {{ (p.titulo_limpio or p.titulo_original) | tojson }}, {{ (p.anio or "") | tojson }}, {{ (p.url or "") | tojson }})'><i class="fa-solid fa-pen"></i> Editar Info</button>
            {% endif %}
            <button class="btn btn-del" onclick="borrarMedio({{ p.id }})"><i class="fa-solid fa-trash"></i> Borrar Entrada</button>
        </div>
    </div>
    {% endfor %}
</div>

<!-- Modal Editor -->
<div id="modalEdit" class="modal">
    <div class="modal-content">
        <span class="close" onclick="cerrarModal('modalEdit')">&times;</span>
        <h2 style="margin-top:0"><i class="fa-solid fa-pen-to-square"></i> Editor de Metadatos y Enlaces</h2>
        <p style="color:#666; font-size:13px; margin-bottom:20px;">Edita el título o inserta un <b>Magnet Link</b> directamente si quieres bajar una temporada/capítulo específico en Latino.</p>
        <input type="hidden" id="editId">
        
        <label>Título (Nombre Oficial)</label>
        <input type="text" id="editTitulo" placeholder="Ej: Zootopia 2">
        
        <label>Año de Salida</label>
        <input type="number" id="editAnio" placeholder="Ej: 2025">
        
        <label>URL / Magnet Link (Para capítulo o temporada específica)</label>
        <input type="text" id="editUrl" placeholder="magnet:?xt=urn:btih:... o link directo">
        
        <button class="btn btn-start" style="width:100%; justify-content:center" onclick="guardarEdicion()"><i class="fa-solid fa-floppy-disk"></i> Guardar y Reintentar</button>
    </div>
</div>

<!-- Modal Video -->
<div id="modalVideo" class="modal">
    <div class="modal-content video-content">
        <span class="close" onclick="cerrarVideo()" style="color:white; top:0; right:10px">&times;</span>
        <video id="videoPlayer" controls style="width:100%; border-radius:10px;"></video>
        <h3 id="videoTitle" style="color:white; margin:15px 0 0 5px; font-weight:600;"></h3>
    </div>
</div>

<script>
    // Configuración visual
    function setView(mode) {
        const container = document.getElementById('main-container');
        const btnGrid = document.getElementById('btn-grid');
        const btnList = document.getElementById('btn-list');
        
        if (mode === 'grid') {
            container.className = 'media-container view-grid';
            btnGrid.classList.add('active');
            btnList.classList.remove('active');
        } else {
            container.className = 'media-container view-list';
            btnList.classList.add('active');
            btnGrid.classList.remove('active');
        }
    }

    // Filtrado de Cards
    function filterCards(filterType, btnElem) {
        // Actualizar UI de botones
        document.querySelectorAll('.filters .filter-btn').forEach(btn => btn.classList.remove('active'));
        btnElem.classList.add('active');
        
        // Filtrar elementos
        const cards = document.querySelectorAll('.item-card');
        cards.forEach(card => {
            const tipo = card.getAttribute('data-tipo');
            const estado = card.getAttribute('data-estado');
            
            if (filterType === 'all') {
                card.style.display = '';
            } else if (filterType === 'pelicula' || filterType === 'serie') {
                card.style.display = (tipo.includes(filterType)) ? '' : 'none';
            } else {
                card.style.display = (estado === filterType) ? '' : 'none';
            }
        });
    }

    // API Funciones
    function iniciarDescargas(btn) {
        // Lógica de feedback visual
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Iniciando...';
        fetch('/api/iniciar_descargas', { method: 'POST' })
        .then(r => r.json()).then(d => { alert(d.mensaje); location.reload(); });
    }

    function borrarTodoBD() {
        if(!confirm(`⚠️ ¡ADVERTENCIA CRÍTICA! ⚠️\n\n¿Estás seguro de que deseas BORRAR TODA LA BASE DE DATOS?\nEsto eliminará del bot tanto las películas pendientes como el registro de las completadas.\n\nEsta acción NO se puede deshacer.`)) return;
        
        fetch('/api/borrar_todo', { method: 'POST' })
        .then(r => r.json()).then(d => { 
            alert(d.mensaje); 
            location.reload(); 
        });
    }

    function purgarErrores() {
        if(!confirm(`¿Seguro que quieres borrar todas las películas con error?\nEsto no se puede deshacer.`)) return;
        fetch('/api/purgar_errores', { method: 'POST' })
        .then(r => r.json()).then(d => { location.reload(); });
    }

    function borrarMedio(id) {
        if(!confirm("¿Eliminar este registro permanentemente de la lista?")) return;
        fetch(`/api/borrar_medio/${id}`, { method: 'POST' })
        .then(r => r.json()).then(d => { location.reload(); });
    }

    // Modales
    function abrirEditor(id, titulo, anio, url) {
        document.getElementById('editId').value = id;
        document.getElementById('editTitulo').value = titulo;
        document.getElementById('editAnio').value = anio;
        document.getElementById('editUrl').value = url || '';
        document.getElementById('modalEdit').style.display = 'flex';
    }

    function cerrarModal(id) { document.getElementById(id).style.display = 'none'; }

    function guardarEdicion() {
        const id = document.getElementById('editId').value;
        const data = {
            titulo: document.getElementById('editTitulo').value,
            anio: document.getElementById('editAnio').value,
            url: document.getElementById('editUrl').value
        };
        fetch(`/api/editar_metadatos/${id}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(data)
        }).then(r => r.json()).then(d => { location.reload(); });
    }

    function verVideo(id, titulo) {
        const player = document.getElementById('videoPlayer');
        player.src = `/play_video/${id}`;
        document.getElementById('videoTitle').innerText = titulo;
        document.getElementById('modalVideo').style.display = 'flex';
        player.play();
    }

    function cerrarVideo() {
        const player = document.getElementById('videoPlayer');
        player.pause();
        player.src = "";
        cerrarModal('modalVideo');
    }
</script>

</body>
</html>
"""

@app.route("/")
def index():
    peliculas = obtener_todos()
    progreso_qbt = obtener_progreso_torrents()
    
    # Mapear progreso a IDs de pelis (usando coincidencia de nombre)
    torrents_info = {}
    for p in peliculas:
        # Buscamos si el nombre de la peli está en los torrents activos
        nombre_clave = p['titulo_limpio'] or p['titulo_original']
        for t_name, t_data in progreso_qbt.items():
            if nombre_clave in t_name:
                torrents_info[str(p['id'])] = t_data
                break

    return render_template_string(HTML_TEMPLATE, peliculas=peliculas, torrents_info=torrents_info)

@app.route("/api/iniciar_descargas", methods=["POST"])
def iniciar_descargas_api():
    global descargando
    if descargando:
        return jsonify({"mensaje": "Ya hay una descarga en curso."}), 400
        
    pendientes = obtener_pendientes()
    if not pendientes:
        return jsonify({"mensaje": "No hay películas pendientes."}), 200

    descargando = True
    
    def run_and_reset():
        global descargando
        try:
            procesar_descargas_pendientes(pendientes)
        finally:
            descargando = False

    threading.Thread(target=run_and_reset).start()
    return jsonify({"mensaje": "Proceso de descarga multihilo iniciado."})

@app.route("/api/purgar_errores", methods=["POST"])
def api_purgar():
    cantidad = eliminar_errores()
    return jsonify({"mensaje": f"Se eliminaron {cantidad} registros con error."})

@app.route("/api/borrar_todo", methods=["POST"])
def api_borrar_todo():
    from src.database import borrar_todo
    cantidad = borrar_todo()
    return jsonify({"mensaje": f"Se borró TODA la base de datos ({cantidad} registros eliminados)."})

@app.route("/api/editar_metadatos/<int:id_medio>", methods=["POST"])
def api_editar(id_medio):
    data = request.json
    actualizar_metadatos(id_medio, data['titulo'], data['anio'], url=data.get('url'))
    return jsonify({"status": "ok"})

@app.route("/api/borrar_medio/<int:id_medio>", methods=["POST"])
def api_borrar(id_medio):
    eliminar_medio(id_medio)
    return jsonify({"status": "ok", "mensaje": "Medio eliminado."})

@app.route("/play_video/<int:id_medio>")
def play_video(id_medio):
    item = obtener_por_id(id_medio)
    if not item or not item['ruta_carpeta']:
        return "Video no encontrado", 404
        
    # Buscar el primer mp4 en la carpeta
    archivos = [f for f in os.listdir(item['ruta_carpeta']) if f.endswith(".mp4")]
    if not archivos:
        return "Archivo MP4 no encontrado", 404
        
    path_video = os.path.join(item['ruta_carpeta'], archivos[0])
    return send_file(path_video, mimetype='video/mp4', as_attachment=False, conditional=True)

def run_server():
    print("Iniciando Panel Web en http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)

