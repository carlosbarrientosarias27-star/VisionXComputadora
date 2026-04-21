# app_1.py — Primera versión funcional con Ollama
import os 
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

def clasificar_imagen_local(img: str, categorias: list) -> dict:
    """
    Clasifica una imagen usando Ollama localmente.
    """
    try:
        # 1. Leer y codificar imagen a Base64
        with open(img, "rb") as f:
            imagen_base64 = base64.b64encode(f.read()).decode("utf-8")

        # 2. Construir el prompt (similar al original pero adaptado a LLaVA)
        prompt_texto = f"""
        Analiza esta imagen y clasifícala en EXACTAMENTE UNA de estas categorías: {', '.join(categorias)}.
        
       Responde ÚNICAMENTE en formato JSON con la siguiente estructura:
        {{
            "categoria": "nombre_de_la_categoria",
            "confianza": valor_numerico_0_a_1,
            "razones": "explicación detallada en español"
        }}
    
        Si no estás seguro o la imagen no coincide con ninguna categoría,
    responde con categoria: "desconocido"
    IMPORTANTE: La explicación de 'razones' debe ser en español.
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

    except Exception as e:
        return {
            "categoria": "error", 
            "confianza": 0, 
            "razones": f"Error: {str(e)}"
        }





# --- PRUEBA DE EJECUCIÓN ---
if __name__ == "__main__":
    carpeta_fotos = "img"
    carpeta_logs = "logs"

    
    if os.path.exists(carpeta_fotos):
        # Obtenemos la lista de todas las imágenes
        archivos = [f for f in os.listdir(carpeta_fotos) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if archivos:
            print(f"INFO: Se han encontrado {len(archivos)} imágenes en '{carpeta_fotos}'.")
            print(f"🤖 Usando modelo: {MODELO_VISION}\n")
            print("-" * 50)

            tiempos = []

            for archivo in archivos:
                ruta_completa = os.path.join(carpeta_fotos, archivo)
                print(f"📸 Procesando: {archivo}...")
                
                inicio = time.time()
                resultado = clasificar_imagen_local(ruta_completa, CATEGORIAS_POR_DEFECTO)
                fin = time.time()                
                duracion = fin - inicio
                tiempos.append(duracion)

                nombre_base = os.path.splitext(archivo)[0]
                ruta_log = f"{archivo}.json"
                ruta_log_txt = os.path.join(carpeta_logs, f"{nombre_base}.txt")

                with open(ruta_log, "w", encoding="utf-8") as f_json:
                    json.dump(resultado, f_json, indent=4, ensure_ascii=False)

                with open(ruta_log_txt, "w", encoding="utf-8") as f_txt:
                    f_txt.write(f"INFORME DE CLASIFICACIÓN\n")
                    f_txt.write(f"{'='*30}\n")
                    f_txt.write(f"Archivo: {archivo}\n")
                    f_txt.write(f"Categoría: {cat.upper()}\n")
                    f_txt.write(f"Confianza: {conf*100:.2f}%\n")
                    f_txt.write(f"Tiempo: {duracion:.2f}s\n")
                    f_txt.write(f"Razones: {razones}\n")
                    f_txt.write(f"{'='*30}\n")

                # Mostrar resultado simplificado en consola
                cat = resultado.get("categoria", "desconocido")
                conf = resultado.get("confianza", 0)
                razones = resultado.get("razones", "Sin explicación disponible")
                print(f"✅ CATEGORÍA: {cat.upper()}")
                print(f"🎯 CONFIANZA: {conf*100:.1f}%")
                print(f"📝 RAZONES: {razones}") 
                print(f"⏱️ TIEMPO: {duracion:.2f}s")
                print("-" * 50)

            # Resumen final
            promedio = sum(tiempos) / len(tiempos)
            print(f"\n📊 RESUMEN DEL LOTE:")
            print(f"⏱️ Tiempo promedio por imagen: {promedio:.2f} segundos")
            print(f"🚀 Tiempo total: {sum(tiempos):.2f} segundos")
            
        else:
            print(f"⚠️ No hay imágenes válidas en '{carpeta_fotos}'.")
    else:
        print(f"❌ La carpeta '{carpeta_fotos}' no existe.")