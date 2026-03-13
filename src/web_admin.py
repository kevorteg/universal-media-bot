from flask import Flask, render_template_string, jsonify, request, send_file, Response
import threading
import os
from src.database import obtener_todos, obtener_pendientes, eliminar_errores, actualizar_metadatos, obtener_por_id
from src.downloader import procesar_descargas_pendientes
from src.qbittorrent_mgr import obtener_progreso_torrents

app = Flask(__name__)

# Variable global para evitar descargas concurrentes
descargando = False

# HTML Embebido extendido con Modales y Reproductor
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PelisCristianas Bot - Admin Premium</title>
    <style>
        :root { --primary: #3498db; --secondary: #2ecc71; --danger: #e74c3c; --dark: #2c3e50; }
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }
        .header { display: flex; justify-content: space-between; align-items: center; background: white; padding: 15px 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 30px; }
        h1 { margin: 0; font-size: 24px; color: var(--dark); }
        .controls { display: flex; gap: 10px; }
        .btn { border: none; padding: 10px 18px; border-radius: 8px; cursor: pointer; font-weight: 600; transition: all 0.2s; }
        .btn-start { background: var(--secondary); color: white; }
        .btn-purge { background: var(--danger); color: white; }
        .btn-edit { background: #f1c40f; color: #2c3e50; font-size: 12px; padding: 5px 10px; }
        .btn-play { background: var(--primary); color: white; margin-top: 10px; width: 100%; }
        .btn:hover { opacity: 0.9; transform: translateY(-1px); }
        
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 25px; }
        .card { background: white; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); transition: transform 0.3s; position: relative; }
        .card:hover { transform: translateY(-5px); }
        .card img { width: 100%; height: 320px; object-fit: cover; background: #ddd; }
        .card-body { padding: 15px; }
        .title { font-weight: bold; font-size: 15px; color: var(--dark); margin-bottom: 4px; display: block; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
        .info { font-size: 12px; color: #666; margin-bottom: 8px; }
        
        .badge { position: absolute; top: 12px; right: 12px; padding: 4px 10px; border-radius: 6px; font-size: 11px; font-weight: bold; color: white; z-index: 10; }
        .badge-pendiente { background: #f39c12; }
        .badge-completada { background: var(--secondary); }
        .badge-error { background: var(--danger); }
        .badge-descargando { background: var(--primary); animation: pulse 1.5s infinite; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        /* Modales */
        .modal { display: none; position: fixed; z-index: 1000; left: 0; top: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); align-items: center; justify-content: center; }
        .modal-content { background: white; padding: 25px; border-radius: 15px; width: 90%; max-width: 500px; position: relative; }
        .video-content { max-width: 900px; padding: 10px; background: black; }
        .close { position: absolute; top: 10px; right: 20px; font-size: 30px; cursor: pointer; color: #aaa; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
    </style>
</head>
<body>

<div class="header">
    <h1>🎬 Panel de Control Bot</h1>
    <div class="controls">
        <button class="btn btn-purge" onclick="purgarErrores()">🗑 Purgar Errores</button>
        <button class="btn btn-start" onclick="iniciarDescargas()">▶ Iniciar Descargas</button>
    </div>
</div>

<div class="grid">
    {% for p in peliculas %}
    <div class="card">
        {% set status_class = 'completada' if p.estado == 'completada' else ('error' if 'error' in p.estado else ('descargando' if p.estado == 'descargando' else 'pendiente')) %}
        <span class="badge badge-{{ status_class }}">
            {{ p.estado|upper }}
        </span>
        <img src="{{ p.poster_url if p.poster_url else 'https://via.placeholder.com/250x350?text=Sin+Poster' }}" alt="Poster">
        <div class="card-body">
            <span class="title">{{ p.titulo_limpio or p.titulo_original }}</span>
            <div class="info">{{ p.anio or 'S/A' | upper }} | {{ p.tipo|capitalize }}</div>
            
            {% if p.id|string in torrents_info %}
                <div style="background:#eee; height:8px; border-radius:4px; margin:8px 0; overflow:hidden;">
                    <div style="background:var(--secondary); height:100%; width:{{ torrents_info[p.id|string].progress }}%;"></div>
                </div>
                <div style="font-size:10px; color:var(--secondary); margin-bottom:10px;">
                     qBT: {{ torrents_info[p.id|string].progress }}% - {{ torrents_info[p.id|string].state }}
                </div>
            {% endif %}

            {% if p.estado == 'completada' %}
                <button class="btn btn-play" onclick="verVideo({{ p.id }}, '{{ (p.titulo_limpio or p.titulo_original)|replace("'", "\\'") }}')">📺 Ver Previa</button>
            {% else %}
                <button class="btn btn-edit" onclick="abrirEditor({{ p.id }}, '{{ (p.titulo_limpio or p.titulo_original)|replace("'", "\\'") }}', '{{ p.anio or "" }}')">✎ Editar</button>
            {% endif %}
        </div>
    </div>
    {% endfor %}
</div>

<!-- Modal Editor -->
<div id="modalEdit" class="modal">
    <div class="modal-content">
        <span class="close" onclick="cerrarModal('modalEdit')">&times;</span>
        <h2>Editar Metadatos</h2>
        <input type="hidden" id="editId">
        <label>Título Limpio</label>
        <input type="text" id="editTitulo" placeholder="Ej: La Pasión de Cristo">
        <label>Año</label>
        <input type="number" id="editAnio" placeholder="Ej: 2004">
        <button class="btn btn-start" style="width:100%" onclick="guardarEdicion()">Guardar y Reintentar</button>
    </div>
</div>

<!-- Modal Video -->
<div id="modalVideo" class="modal">
    <div class="modal-content video-content">
        <span class="close" onclick="cerrarVideo()" style="color:white">&times;</span>
        <video id="videoPlayer" controls style="width:100%"></video>
        <h3 id="videoTitle" style="color:white; margin:10px 0 0 10px"></h3>
    </div>
</div>

<script>
    function iniciarDescargas() {
        fetch('/api/iniciar_descargas', { method: 'POST' })
        .then(r => r.json()).then(d => { alert(d.mensaje); location.reload(); });
    }

    function purgarErrores() {
        if(!confirm("¿Seguro que quieres borrar todas las películas con error?")) return;
        fetch('/api/purgar_errores', { method: 'POST' })
        .then(r => r.json()).then(d => { alert(d.mensaje); location.reload(); });
    }

    function abrirEditor(id, titulo, anio) {
        document.getElementById('editId').value = id;
        document.getElementById('editTitulo').value = titulo;
        document.getElementById('editAnio').value = anio;
        document.getElementById('modalEdit').style.display = 'flex';
    }

    function cerrarModal(id) { document.getElementById(id).style.display = 'none'; }

    function guardarEdicion() {
        const id = document.getElementById('editId').value;
        const data = {
            titulo: document.getElementById('editTitulo').value,
            anio: document.getElementById('editAnio').value
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

@app.route("/api/editar_metadatos/<int:id_medio>", methods=["POST"])
def api_editar(id_medio):
    data = request.json
    actualizar_metadatos(id_medio, data['titulo'], data['anio'])
    return jsonify({"status": "ok"})

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

