# app_1.py — Primera versión funcional con Ollama
import requests
import base64
import json
import time
from config import (
    MODELO_VISION, 
    OLLAMA_URL, 
    CONFIG_CONSISTENTE, 
    TIMEOUT, 
    CATEGORIAS_POR_DEFECTO
)

def clasificar_imagen_local(ruta_imagen: str, categorias: list) -> dict:
    """
    Clasifica una imagen usando Ollama localmente.
    """
    try:
        # 1. Leer y codificar imagen a Base64
        with open(ruta_imagen, "rb") as f:
            imagen_base64 = base64.b64encode(f.read()).decode("utf-8")

        # 2. Construir el prompt (similar al original pero adaptado a LLaVA)
        prompt_texto = f"""
        Analyze this image and classify it into EXACTLY ONE of these categories: {', '.join(categorias)}.
        
        Return ONLY a JSON object with:
        - "categoria": the chosen category
        - "confianza": a number between 0 and 1
        - "razones": a short explanation
        
        If unsure, use "desconocido".
        """

        # 3. Preparar el payload para la API de Ollama
        payload = {
            "model": MODELO_VISION,
            "prompt": prompt_texto,
            "images": [imagen_base64],
            "format": "json",  # Forzamos salida JSON si el modelo lo soporta
            "options": CONFIG_CONSISTENTE,
            "stream": False
        }

        # 4. Realizar la petición POST
        response = requests.post(OLLAMA_URL, json=payload, timeout=TIMEOUT)
        response.raise_for_status()
        
        # 5. Procesar respuesta
        full_response = response.json()
        respuesta_texto = full_response.get("response", "{}")
        
        return json.loads(respuesta_texto)

    except FileNotFoundError:
        return {"categoria": "error", "confianza": 0, "razones": f"Archivo no encontrado: {ruta_imagen}"}
    except requests.exceptions.RequestException as e:
        return {"categoria": "error", "confianza": 0, "razones": f"Error de conexión con Ollama: {str(e)}"}
    except Exception as e:
        return {
            "categoria": "error", 
            "confianza": 0, 
            "razones": f"Error inesperado: {str(e)}",
            "raw": locals().get('respuesta_texto', 'No response')
        }

# --- PRUEBA DE EJECUCIÓN ---
if __name__ == "__main__":
    # Asegúrate de tener una imagen de prueba llamada 'test.jpg' o cambia la ruta
    imagen_test = "test.jpg" 
    
    print(f"--- Clasificando con modelo: {MODELO_VISION} ---")
    inicio = time.time()
    
    resultado = clasificar_imagen_local(imagen_test, CATEGORIAS_POR_DEFECTO)
    
    fin = time.time()
    
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(f"\n⏱️ Tiempo de respuesta: {fin - inicio:.2f} segundos")