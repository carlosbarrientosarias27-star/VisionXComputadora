# Documentación de Cambios: Sistema de Clasificación Local (v1.1)
Esta versión de app_1.py mejora la capacidad del script para procesar múltiples imágenes de forma secuencial, garantizando la persistencia de los datos y la correcta codificación del idioma español.

## 📋 Resumen de Cambios
Soporte Multi-Archivo: Transición de procesar una sola imagen a iterar sobre una carpeta completa.

Sistema de Logging JSON: Exportación automática de cada resultado a la carpeta logs/.

Internacionalización (Español): Refuerzo del prompt para asegurar respuestas en castellano.

Manejo de Errores Robusto: Captura de excepciones mejorada para evitar interrupciones durante el proceso por lotes.

## 🛠️ Detalle de los Cambios Paso a Paso

### 1. Refuerzo del Idioma y Formato (Función clasificar_imagen_local)
Se modificó el prompt_texto para ser más explícito con el modelo de IA:

Instrucción de Formato: Se definió un esquema JSON estricto ("categoria", "confianza", "razones").

Localización: Se añadió la instrucción específica IMPORTANTE: La explicación de 'razones' debe ser en español.

Consistencia: Se incluyó el parámetro "format": "json" en el payload para forzar al modelo a devolver datos estructurados.

### 2. Automatización de la Carpeta de Logs
En el bloque principal (if __name__ == "__main__":), se añadieron líneas para gestionar el almacenamiento:

Variable carpeta_logs: Se definió el directorio donde se guardarán los resultados.

Creación Automática: Se utiliza os.makedirs (o validación previa) para asegurar que la carpeta existe antes de intentar escribir en ella.

### 3. Implementación del Bucle de Procesamiento
Se sustituyó la llamada única por un bucle for:

Filtro de Extensiones: El script ahora busca activamente archivos .jpg, .jpeg y .png.

Gestión de Rutas: Uso de os.path.join para construir rutas de archivos compatibles con cualquier sistema operativo (Windows/Linux).

### 4. Persistencia de Resultados (Escritura JSON)
Después de procesar cada imagen, se implementó el guardado físico:

Pitón
nombre_log = f"{archivo}.json"
ruta_log = os.path.join(carpeta_logs, nombre_log)

with open(ruta_log, "w", encoding="utf-8") as f_json:
    json.dump(resultado, f_json, indent=4, ensure_ascii=False)
encoding="utf-8": Crucial para que los acentos y la "ñ" se guarden correctamente.

ensure_ascii=False: Evita que los caracteres especiales se conviertan a códigos Unicode (ej: de \u00f1 a ñ).

indent=4: Hace que los archivos generados sean legibles para humanos.

### 5. Interfaz de Terminal Mejorada
Se actualizó la salida por consola para mostrar la información completa extraída:

Categoría: Se muestra en mayúsculas (.upper()).

Confianza: Se formatea de decimal (0.85) a porcentaje (85.0%).

Razones: Se imprime la explicación detallada que antes se omitía.

Métricas: Se mantiene el seguimiento del tiempo por imagen y el resumen total del lote.

## 🚀 Cómo ejecutar esta versión
Asegúrate de tener la carpeta img/ con tus imágenes.

Configura las variables en config.py (especialmente OLLAMA_URL y MODELO_VISION).

Ejecuta: python app_1.py.

Revisa la carpeta logs/ para ver los resultados individuales.