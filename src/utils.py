def sanitize_filename(title):
    """
    Limpia el título para evitar caracteres no válidos en el sistema de archivos
    (Windows/Linux/Mac).
    """
    if not title:
        return "Desconocido"
        
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        title = title.replace(char, "_")
        
    return title.strip()
