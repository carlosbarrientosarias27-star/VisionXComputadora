# Documentación de Cambios: Sistema de Clasificación Local con Logs Duales
Esta guía detalla la evolución del script app_1.py desde su versión inicial hasta la implementación actual, que incluye procesamiento por lotes, exportación de resultados y soporte completo en español.

## 📋 Resumen de la Versión Final
El script ahora es capaz de escanear una carpeta de imágenes, procesarlas individualmente usando el modelo de visión de Ollama y generar dos tipos de informes (JSON y TXT) por cada archivo.

## 🛠️ Detalle de los Cambios Paso a Paso

### 1. Optimización del Prompt (Idioma y Formato)
Se modificó la lógica interna de la función clasificar_imagen_local para asegurar resultados consistentes:

Forzado de Idioma: Se añadieron instrucciones explícitas (IMPORTANTE: La explicación de 'razones' debe ser en español) para evitar respuestas en inglés.

Estructura JSON estricta: Se definió un esquema con las llaves categoria, confianza y razones para facilitar la lectura automática.

### 2. Implementación de Procesamiento por Lotes (Batch)

Se sustituyó la ejecución de una única imagen por un bucle for que automatiza el trabajo:

Escaneo de Directorio: El script busca todos los archivos en la carpeta img/.

Filtro de Extensiones: Se añadió una validación para procesar únicamente archivos .jpg, .jpeg y .png.

### 3. Sistema de Persistencia Dual (Logs)

Se implementó un sistema de guardado doble para cada imagen procesada:

Extracción de Nombre Base: Usamos os.path.splitext(archivo)[0] para obtener el nombre del archivo sin la extensión (ej. de foto1.jpg a foto1).

Archivo JSON: Guarda la respuesta completa del modelo para uso técnico o integraciones futuras.

Archivo TXT: Crea un informe legible para humanos con el siguiente formato:

Encabezado decorativo (===).

Datos clave (Archivo, Categoría en mayúsculas, % de confianza, Tiempo de ejecución).

Explicación detallada de las razones.

### 4. Codificación y Robustez
UTF-8: Se configuró encoding="utf-8" en todas las aperturas de archivos para que las tildes y eñes se guarden correctamente.

Manejo de Tiempos: Se integró el módulo time para calcular cuánto tarda el modelo en procesar cada imagen y mostrar un resumen final del lote.

## 📂 Estructura de Salida Generada
Tras ejecutar el script, la carpeta logs/ contendrá:

nombre_imagen.json → Datos estructurados.

nombre_imagen.txt → Reporte de lectura rápida.

Ejemplo de reporte TXT:

Plaintext
INFORME DE CLASIFICACIÓN
==============================
Archivo: gato.jpg
Categoría: ANIMAL
Confianza: 98.50%
Tiempo: 2.15s
Razones: Se observa un felino doméstico con pelaje atigrado sobre un sofá.
==============================

## 🚀 Cómo usar esta versión
Coloca tus imágenes en la carpeta img/.

Asegúrate de que Ollama esté corriendo con el modelo especificado en tu config.py.

Ejecuta el script: python app_1.py.

Revisa los resultados en la carpeta logs/.