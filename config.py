# config.py — configuración compartida terminal + interfaz

# --- MODELOS ---
MODELO_VISION = 'llava:7b'
MODELOS_DISPONIBLES = ['llava:7b', 'moondream']    
OLLAMA_URL    = 'http://localhost:11434/api/generate'

# Parámetros para garantizar consistencia
CONFIG_CONSISTENTE = {
    'temperature': 0.0,    # Cero aleatoriedad para respuestas deterministas
    'seed': 42,            # Semilla fija para reproducibilidad
    'num_predict': 150,    # Límite de tokens en la respuesta
    'top_k': 1,            # Tomar siempre la palabra más probable
    'top_p': 0.9,
    'repeat_penalty': 1.2, # Evita que el modelo se buclee en una palabra
    'stream': False        # Necesario para recibir el JSON completo de una vez
}

# --- SISTEMA Y RUTAS ---
TIMEOUT            = 120   # Los modelos de visión pueden tardar en procesar
MAX_REINTENTOS     = 3
CARPETA_IMAGENES   = 'img'
CARPETA_RESULTADOS = 'resultados'

# --- CATEGORÍAS ---
CATEGORIAS_POR_DEFECTO = [
    'gato', 'perro', 'pajaro', 'auto',
    'comida', 'persona', 'flor', 'arbol',
    'casa', 'desconocido'
]