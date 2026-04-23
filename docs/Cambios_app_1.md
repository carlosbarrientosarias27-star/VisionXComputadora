# 📝 Registro de Cambios: VisionXApp (demo_app.py)
Este documento resume las actualizaciones realizadas en la aplicación de clasificación de imágenes basada en IA local (Ollama).

## 1. 🏗 Estructura y Robustez de Configuración
Importación Blindada: Se añadió un bloque try-except para importar el archivo config.py. En caso de que no exista, la aplicación ahora genera automáticamente una clase interna con valores por defecto para evitar que el programa falle al iniciar.

Ajuste de Path: Se implementó lógica para detectar el directorio raíz, permitiendo que la aplicación se ejecute correctamente independientemente de si se lanza desde la carpeta principal o una subcarpeta.

## 2. 🎨 Mejoras en la Interfaz de Usuario (UI)
Vista Previa de Imágenes: Al seleccionar archivos, el label drop_lbl ya no solo muestra texto; ahora genera una miniatura real (thumbnail) de la primera imagen seleccionada usando la librería PIL.

Estado del Servidor: Se añadió un status_badge dinámico ("✓ Ollama listo") para dar feedback visual sobre el estado del servicio.

Panel de Resultados Estilizado: Se rediseñó la columna derecha para incluir una "barra de pestañas" simulada con botones para cambiar entre vistas de Resultados, JSON y TXT.

Modo Oscuro Persistente: Se configuró el tema dark y el color blue de customtkinter para una estética moderna y profesional.

## 3. 🧠 Lógica de Clasificación e IA
Prompt Engineering Optimizado: Se mejoró el prompt enviado a Llava para exigir un formato de respuesta estricto:

CATEGORÍA:

CONFIANZA:

RAZONES:

Extracción de Datos mediante Regex: Se implementó una lógica de extracción robusta que utiliza expresiones regulares (re) para capturar la categoría y la confianza, incluso si el modelo de lenguaje añade texto extra o varía ligeramente el formato.

Manejo de Porcentajes: Se corrigió el tratamiento de la confianza. Ahora el sistema acepta valores de 0 a 100 y los convierte internamente a flotantes (0.0 a 1.0) para una gestión de datos más estandarizada.

## 4. 📂 Gestión de Archivos y Auto-guardado
Sistema de Sesiones: Al iniciar una clasificación, el sistema crea una carpeta única basada en el timestamp: resultados/proceso_YYYYMMDD_HHMMSS/.

Auto-guardado Granular: * Cada imagen procesada se guarda instantáneamente en carpetas individuales de /json y /txt.

Esto evita la pérdida de datos si el proceso se interrumpe a mitad de una lista larga de imágenes.

Exportación Global: Se mantuvieron y mejoraron las funciones guardar_json y guardar_txt para que el usuario pueda exportar el resumen completo de la sesión de forma manual con diálogos de guardado estándar.

## 5. 🛠 Estabilidad y Depuración
Multithreading: La clasificación se ejecuta en un hilo (threading.Thread) separado. Esto evita que la interfaz de la ventana se congele ("No responde") mientras la IA procesa las imágenes.

Logs en Consola: Se añadieron impresiones detalladas ([DEBUG], [AUTO-SAVE]) para que el desarrollador pueda monitorear el flujo de datos y los tiempos de respuesta de la API en tiempo real.

Validación de Entradas: Se añadieron chequeos para asegurar que las rutas de imagen y las categorías sean válidas antes de intentar realizar la petición HTTP.