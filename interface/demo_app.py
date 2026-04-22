import os
import sys 
import threading
import base64
import requests
import json
import time 
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from datetime import datetime

# --- ARREGLO DE IMPORTACIÓN PARA CONFIG.PY ---
directorio_actual = os.path.dirname(os.path.abspath(__file__))
directorio_raiz = os.path.dirname(directorio_actual)
if directorio_raiz not in sys.path:
    sys.path.append(directorio_raiz)

try:
    import config  #
except ModuleNotFoundError:
    class config:
        CATEGORIAS_POR_DEFECTO = ['gato', 'perro', 'pajaro', 'auto',
                                  'comida', 'persona', 'flor', 'arbol',
                                  'casa', 'desconocido']
        OLLAMA_URL = "http://localhost:11434/api/generate"
        MODELO_VISION = "llava"
        TIMEOUT = 300
        CONFIG_CONSISTENTE = {
            "temperature": 0.2,
            "seed": 42,
            "num_predict": 150,
            "top_k": 40,
            "top_p": 0.9,
            "repeat_penalty": 1.1,
            "stream": False
        }

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VisionXApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VisionXComputadora - Clasificador")
        self.geometry("1150x750")
        self.configure(fg_color="#181818")

        self.imagenes_seleccionadas = []    
        self.resultados_clasificacion = []  
        self.clasificando = False          

        # --- UI LAYOUT ---
        self.setup_ui()
        
        # --- VINCULACIÓN DE LÓGICA ---
        self.setup_logic()

    def setup_ui(self):
        # Cabecera
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", pady=(15, 5))

        self.logo = ctk.CTkLabel(self.header, text="🌀 VisionXComputadora", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo.pack()

        # Badge de estado con el icono de check como en la imagen
        self.status_badge = ctk.CTkLabel(self.header, text="✓ Ollama listo", text_color="#4cd137", font=ctk.CTkFont(size=12))
        self.status_badge.pack()

        # Contenedor Principal
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Columna Izquierda
        self.left_col = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_col.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # 1. Card Categorías
        cat_card = ctk.CTkFrame(self.left_col, fg_color="#252525", corner_radius=10, border_width=1, border_color="#333")
        cat_card.pack(fill="x", pady=(0, 15), ipady=10)
        ctk.CTkLabel(cat_card, text="🗂 Categorías", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=10)

        # Tags horizontales vinculados a cargar_preset
        tag_bar = ctk.CTkFrame(cat_card, fg_color="transparent")
        tag_bar.pack(fill="x", padx=15)
        
        quick_tags = ["🐾 Animales", "📦 Objetos", "🌳 Naturaleza", "👤 Personas"]
        for text in quick_tags:
            btn = ctk.CTkButton(tag_bar, text=text, width=85, height=28, corner_radius=6, font=ctk.CTkFont(size=11),
                                command=lambda t=text: self.cargar_preset(t)) #
            btn.pack(side="left", padx=2)

        # Entrada de texto y botón +
        entry_row = ctk.CTkFrame(cat_card, fg_color="transparent")
        entry_row.pack(fill="x", padx=15, pady=10)
        self.cat_entry = ctk.CTkEntry(entry_row, placeholder_text="Nueva categoría...", height=35, fg_color="#1e1e1e")
        self.cat_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.add_btn = ctk.CTkButton(entry_row, text="+", width=35, height=35, fg_color="#44bd32")
        self.add_btn.pack(side="right")

        self.cat_display = ctk.CTkTextbox(cat_card, height=70, fg_color="#1a1a1a", font=("Consolas", 12))
        self.cat_display.pack(fill="x", padx=15)
        self.cat_display.insert("0.0", ", ".join(config.CATEGORIAS_POR_DEFECTO)) #

        # 2. Card Imágenes
        img_card = ctk.CTkFrame(self.left_col, fg_color="#252525", corner_radius=10, border_width=1, border_color="#333")
        img_card.pack(fill="both", expand=True)
        ctk.CTkLabel(img_card, text="📸 Imágenes", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=15, pady=10)

        btn_row = ctk.CTkFrame(img_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=15)
        self.select_btn = ctk.CTkButton(btn_row, text="📁 Seleccionar", fg_color="#3498db", height=35)
        self.select_btn.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.clear_btn = ctk.CTkButton(btn_row, text="🗑 Limpiar", fg_color="#e84118", height=35)
        self.clear_btn.pack(side="right", fill="x", expand=True)

        self.drop_lbl = ctk.CTkLabel(img_card, text="No hay imágenes seleccionadas", text_color="#7f8c8d")
        self.drop_lbl.pack(expand=True)

        # --- COLUMNA DERECHA (Panel de Resultados con Pestañas) ---
        self.right_col = ctk.CTkFrame(self.main_container, fg_color="#252525", corner_radius=10, border_width=1, border_color="#333")
        self.right_col.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Barra de pestañas flotante superior
        self.tab_container = ctk.CTkFrame(self.right_col, fg_color="transparent")
        self.tab_container.pack(fill="x", pady=(15, 0))
        
        # Centrar los botones de pestañas
        self.tab_inner = ctk.CTkFrame(self.tab_container, fg_color="#333", corner_radius=8)
        self.tab_inner.pack(anchor="center")

        self.btn_res = ctk.CTkButton(self.tab_inner, text="📊 Resultados", width=100, height=30, corner_radius=6, fg_color="#3498db")
        self.btn_res.pack(side="left", padx=2, pady=2)
        
        self.btn_json = ctk.CTkButton(self.tab_inner, text="📄 JSON", width=70, height=30, corner_radius=6, fg_color="transparent", text_color="#aaa")
        self.btn_json.pack(side="left", padx=2, pady=2)
        
        self.btn_txt = ctk.CTkButton(self.tab_inner, text="📝 TXT", width=70, height=30, corner_radius=6, fg_color="transparent", text_color="#aaa")
        self.btn_txt.pack(side="left", padx=2, pady=2)

        # Área de texto con margen superior para dar el efecto de la imagen
        self.result_area = ctk.CTkTextbox(self.right_col, fg_color="#1a1a1a", corner_radius=8, border_width=1, border_color="#333")
        self.result_area.pack(fill="both", expand=True, padx=20, pady=(15, 20))

        # --- BOTÓN INFERIOR ---
        self.classify_btn = ctk.CTkButton(self, text="🚀 CLASIFICAR", height=50, 
                                        font=ctk.CTkFont(size=15, weight="bold"),
                                        fg_color="#44bd32", hover_color="#2ecc71")
        self.classify_btn.pack(fill="x", padx=20, pady=20)

    def setup_logic(self):
        self.add_btn.configure(command=self.agregar_categoria_manual)
        self.select_btn.configure(command=self.seleccionar_imagenes)
        self.clear_btn.configure(command=self.limpiar_imagenes)
        self.classify_btn.configure(command=self.iniciar_clasificacion)
        self.btn_json.configure(command=self.guardar_json)
        self.btn_txt.configure(command=self.guardar_txt)

    # ---------- MANEJO DE CATEGORÍAS ----------
    def agregar_categoria_manual(self):
        nueva = self.cat_entry.get().strip()
        if nueva:
            contenido_actual = self.cat_display.get("0.0", "end").strip()
            separador = ", " if contenido_actual else ""
            self.cat_display.insert("end", f"{separador}{nueva}")
            self.cat_entry.delete(0, "end")

    def cargar_preset(self, tipo):
        presets = {
            "🐾 Animales": "gato, perro, pajaro, tigre, leon",
            "📦 Objetos": "auto, bicicleta, mesa, silla, botella",
            "🌳 Naturaleza": "flor, arbol, montaña, rio, bosque",
            "👤 Personas": "hombre, mujer, niño, niña, grupo"
        }
        self.cat_display.delete("0.0", "end")
        self.cat_display.insert("0.0", presets.get(tipo, "desconocido"))

    # ---------- MANEJO DE IMÁGENES ----------
    def seleccionar_imagenes(self):
        files = ctk.filedialog.askopenfilenames(title="Seleccionar imágenes",
                                                filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")])
        if files:
            self.imagenes_seleccionadas = list(files)
            self.drop_lbl.configure(text=f"✅ {len(files)} imágenes seleccionadas", text_color="#4cd137")

    def limpiar_imagenes(self):
        self.imagenes_seleccionadas = []
        self.drop_lbl.configure(text="No hay imágenes seleccionadas", text_color="#7f8c8d")

    # ---------- CLASIFICACIÓN ----------
    def iniciar_clasificacion(self):
        if self.clasificando:
            return
        if not self.imagenes_seleccionadas:
            self.result_area.delete("0.0", "end")
            self.result_area.insert("0.0", "❌ ERROR: No has seleccionado ninguna imagen.\n")
            self.result_area.insert("end", "Haz clic en '📁 Seleccionar' primero.")
            return
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.carpeta_sesion_actual = os.path.join(os.getcwd(), "resultados", f"proceso_{timestamp}")

        # Limpiar resultados anteriores
        self.resultados_clasificacion = []
        self.result_area.delete("0.0", "end")
        self.result_area.insert("0.0", "🚀 INICIANDO PROCESO...\n")
        self.result_area.insert("end", f"----------------------------\n")
        self.result_area.insert("end", f"📸 Imágenes detectadas: {len(self.imagenes_seleccionadas)}\n")
        self.result_area.insert("end", f"🏷 Categorías: {self.cat_display.get('0.0', 'end').strip()}\n")
        self.result_area.insert("end", f"----------------------------\n")

        # Deshabilitar botón durante la clasificación
        self.classify_btn.configure(state="disabled", text="⏳ CLASIFICANDO...")
        self.clasificando = True

        hilo = threading.Thread(target=self.clasificar_todas, daemon=True)
        hilo.start()

    def clasificar_todas(self):
        categorias_str = self.cat_display.get("0.0", "end").strip()
        total = len(self.imagenes_seleccionadas)
        
        for idx, ruta in enumerate(self.imagenes_seleccionadas):
            # Actualizar UI (desde el hilo principal)
            self.after(0, lambda i=idx+1, t=total: self.result_area.insert("end", f"🖼 Procesando imagen {i}/{t}...\n"))
            
            resultado = self.clasificar_una_imagen(ruta, categorias_str)
            if resultado:
                self.resultados_clasificacion.append(resultado)
                # Mostrar resumen en el área de resultados
                self.after(0, lambda r=resultado: self.mostrar_resumen_en_ui(r))
                
                # --- NUEVO: GUARDADO INDIVIDUAL POR CADA IMAGEN ---
                self.auto_guardar_individual(resultado) 
            else:
                # Error en la clasificación, añadir un registro de error
                self.resultados_clasificacion.append({
                    "imagen": os.path.basename(ruta),
                    "error": "No se pudo obtener respuesta de Ollama",
                    "timestamp": datetime.now().isoformat()
                })
                self.after(0, lambda: self.result_area.insert("end", f"❌ Error con {os.path.basename(ruta)}\n"))
        
        # Finalizar el proceso general
        self.after(0, self.finalizar_clasificacion)
    
    def auto_guardar_individual(self, res):
        """Guarda los resultados de cada imagen en una carpeta común fija."""
        try:
            # Usamos la carpeta definida al inicio del proceso
            folder_session = self.carpeta_sesion_actual
            
            # Crear las subcarpetas json y txt dentro de esa carpeta única
            for sub in ["json", "txt"]:
                path = os.path.join(folder_session, sub)
                if not os.path.exists(path):
                    os.makedirs(path)

            nombre_limpio = os.path.splitext(res['imagen'])[0]
            
            # Guardar JSON individual
            ruta_json = os.path.join(folder_session, "json", f"{nombre_limpio}.json")
            with open(ruta_json, "w", encoding="utf-8") as f:
                json.dump(res, f, indent=4, ensure_ascii=False)

            # Guardar TXT individual
            ruta_txt = os.path.join(folder_session, "txt", f"{nombre_limpio}.txt")
            with open(ruta_txt, "w", encoding="utf-8") as f:
                f.write(f"RESULTADO: {res['imagen']}\n")
                f.write(f"Fecha: {res['timestamp']}\n")
                f.write("-" * 30 + "\n")
                f.write(f"Categoría: {res['categoria']}\n")
                f.write(f"Confianza: {res['confianza']*100:.1f}%\n")
                f.write(f"Razones: {res['razones']}\n")
                
            print(f"[AUTO] Guardado en carpeta común: {nombre_limpio}")
        except Exception as e:
            print(f"[ERROR AUTO-GUARDADO] {e}")
    
    def clasificar_una_imagen(self, ruta_imagen, categorias_str):
        """Envía una imagen a Ollama y devuelve un diccionario con los resultados."""
        import time
        start_time = time.time()

        # === VALIDACIÓN DE PARÁMETROS ===
        print(f"[DEBUG] Parámetro ruta_imagen recibido: {ruta_imagen}")
        print(f"[DEBUG] Parámetro categorias_str recibido: {categorias_str}")
        print(f"[DEBUG] Tipo ruta_imagen: {type(ruta_imagen)}")
        print(f"[DEBUG] Tipo categorias_str: {type(categorias_str)}")
        
        if not ruta_imagen:
            print("❌ Error: ruta_imagen está vacío o es None")
            return None
        
        if not categorias_str:
            print("❌ Error: categorias_str está vacío o es None")
            return None
        
        if not isinstance(ruta_imagen, str):
            print(f"❌ Error: ruta_imagen debe ser string, es {type(ruta_imagen)}")
            return None
        
        if not isinstance(categorias_str, str):
            print(f"❌ Error: categorias_str debe ser string, es {type(categorias_str)}")
            return None
        
        try:
            # Validaciones iniciales
            if not os.path.exists(ruta_imagen):
                print(f"❌ Error: No existe el archivo {ruta_imagen}")
                return None
                
            with open(ruta_imagen, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Prompt mejorado para obtener el formato deseado
            prompt = f"""Clasifica esta imagen en UNA SOLA de estas categorías: {categorias_str}.
            Responde EXACTAMENTE en este formato (sin texto adicional antes o después):
            CATEGORÍA: <categoría exacta>
            CONFIANZA: <número entre 0 y 100>
            RAZONES: <explicación detallada en español>

            Ejemplo de respuesta correcta:
            CATEGORÍA: GATO
            CONFIANZA: 95.5
            RAZONES: La imagen muestra claramente un felino doméstico con orejas puntiagudas y bigotes característicos, sin elementos que sugieran otra categoría."""
            
            payload = {
                "model": config.MODELO_VISION,
                "prompt": prompt,
                "images": [img_base64],
                **config.CONFIG_CONSISTENTE
            }
            
            respuesta = requests.post(config.OLLAMA_URL, json=payload, timeout=config.TIMEOUT)
            
            elapsed_time = time.time() - start_time
            
            if respuesta.status_code == 200:
                data = respuesta.json()
                texto_respuesta = data.get("response", "").strip()
                
                # Extracción robusta de los campos
                categoria = "desconocida"
                confianza = 0.0
                razones = "No se pudo extraer la explicación"
                
                # Buscar cada campo en el texto
                lines = texto_respuesta.split('\n')
                for line in lines:
                    line = line.strip()
                    if line.startswith("CATEGORÍA:") or line.startswith("CATEGORIA:"):
                        categoria = line.split(":", 1)[1].strip()
                    elif line.startswith("CONFIANZA:"):
                        try:
                            # Extraer número (puede venir con o sin %)
                            confianza_str = line.split(":", 1)[1].strip().replace("%", "")
                            confianza_val = float(confianza_str)
                            confianza = confianza_val / 100.0  # Convertir a 0-1
                        except:
                            confianza = 0.0
                    elif line.startswith("RAZONES:"):
                        razones = line.split(":", 1)[1].strip()
                
                # Si no encontró el formato por líneas, intentar con búsqueda general
                if categoria == "desconocida" and "CATEGORÍA:" in texto_respuesta:
                    import re
                    # Buscar CATEGORÍA: algo
                    match_cat = re.search(r'CATEGOR[IÍ]A:\s*([^\n,]+)', texto_respuesta)
                    if match_cat:
                        categoria = match_cat.group(1).strip()
                    
                    # Buscar CONFIANZA: número
                    match_conf = re.search(r'CONFIANZA:\s*([\d\.]+)', texto_respuesta)
                    if match_conf:
                        try:
                            confianza = float(match_conf.group(1)) / 100.0
                        except:
                            pass
                    
                    # Buscar RAZONES: texto
                    match_raz = re.search(r'RAZONES:\s*(.+?)(?=\n\n|\Z)', texto_respuesta, re.DOTALL)
                    if match_raz:
                        razones = match_raz.group(1).strip()
                
                # Mostrar en consola con el formato deseado
                print(f"\n{'='*50}")
                print(f"📷 IMAGEN: {os.path.basename(ruta_imagen)}")
                print(f"🏷️ CATEGORÍA: {categoria}")
                print(f"🎯 CONFIANZA: {confianza*100:.1f}%")
                print(f"📝 RAZONES: {razones}")
                print(f"⏱️ TIEMPO: {elapsed_time:.2f}s")
                print(f"{'='*50}")
                
                return {
                    "imagen": os.path.basename(ruta_imagen),
                    "ruta_completa": ruta_imagen,
                    "categoria": categoria,
                    "confianza": confianza,  # Float entre 0 y 1
                    "razones": razones,
                    "respuesta_completa": texto_respuesta,
                    "timestamp": datetime.now().isoformat(),
                    "tiempo_procesamiento": elapsed_time
                }
            else:
                print(f"❌ Error HTTP {respuesta.status_code} para {ruta_imagen}")
                return None
                
        except Exception as e:
            print(f"❌ Error procesando {ruta_imagen}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
    
    def mostrar_resumen_en_ui(self, resultado):
        """Inserta un resumen legible en el área de texto."""
        self.result_area.insert("end", f"   {resultado['imagen']}\n")
        self.result_area.insert("end", f"   Categoría: {resultado['categoria']}\n")
        # CORREGIDO: Mostrar como porcentaje en lugar del float
        self.result_area.insert("end", f"   Confianza: {resultado['confianza']*100:.1f}%\n")
        self.result_area.insert("end", f"   Razones: {resultado['razones'][:150]}...\n\n")
        self.result_area.see("end")

    def finalizar_clasificacion(self):
        self.clasificando = False
        self.classify_btn.configure(state="normal", text="🚀 CLASIFICAR")
        
        # --- LÓGICA DE AUTO-GUARDADO AUTOMÁTICO ---
        mensaje_adicional = ""
        if self.resultados_clasificacion:
            try:
                # Crear carpeta 'resultados' si no existe
                folder = os.path.join(os.getcwd(), "resultados")
                if not os.path.exists(folder):
                    os.makedirs(folder)
                
                # Generar nombre único basado en la fecha y hora
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                nombre_archivo = f"clasificacion_{timestamp}.json"
                ruta_final = os.path.join(folder, nombre_archivo)
                
                # Guardar el JSON
                with open(ruta_final, "w", encoding="utf-8") as f:
                    json.dump(self.resultados_clasificacion, f, indent=4, ensure_ascii=False)
                
                mensaje_adicional = f"Y AUTO-GUARDADA en: /resultados/{nombre_archivo}"
                print(f"[AUTO-SAVE] Resultados guardados en: {ruta_final}")
            except Exception as e:
                mensaje_adicional = "(Error en auto-guardado)"
                print(f"[ERROR] No se pudo auto-guardar: {e}")

        # Actualización de la interfaz
        self.result_area.insert("end", f"✅ CLASIFICACIÓN COMPLETADA {mensaje_adicional}.\n")
        self.result_area.insert("end", "Puedes exportar copias adicionales usando 📄 JSON o 📝 TXT.\n")
        self.status_badge.configure(text="✓ Clasificación lista", text_color="#4cd137")
        self.result_area.see("end")
        

    # ---------- GUARDADO DE RESULTADOS ----------
    def guardar_json(self):
        if not self.resultados_clasificacion:
            messagebox.showwarning("Sin datos", "No hay resultados de clasificación para guardar.")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Archivos JSON", "*.json"), ("Todos los archivos", "*.*")],
            title="Guardar resultados como JSON"
        )
        if archivo:
            try:
                with open(archivo, "w", encoding="utf-8") as f:
                    json.dump(self.resultados_clasificacion, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Éxito", f"Resultados guardados en:\n{archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo JSON:\n{str(e)}")

    def guardar_txt(self):
        if not self.resultados_clasificacion:
            messagebox.showwarning("Sin datos", "No hay resultados de clasificación para guardar.")
            return
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Guardar resultados como TXT"
        )
        if archivo:
            try:
                with open(archivo, "w", encoding="utf-8") as f:
                    f.write("RESULTADOS DE CLASIFICACIÓN\n")
                    f.write(f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("="*60 + "\n\n")
                    for idx, res in enumerate(self.resultados_clasificacion, 1):
                        if "error" in res:
                            f.write(f"{idx}. {res['imagen']} - ERROR: {res['error']}\n\n")
                        else:
                            f.write(f"{idx}. Imagen: {res['imagen']}\n")
                            # CORREGIDO: Mostrar como porcentaje en el TXT también
                            f.write(f"   Categoría: {res['categoria']}\n")
                            f.write(f"   Confianza: {res['confianza']*100:.1f}%\n")
                            f.write(f"   Razones: {res['razones']}\n")
                messagebox.showinfo("Éxito", f"Resultados guardados en:\n{archivo}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo TXT:\n{str(e)}")


if __name__ == "__main__":
    app = VisionXApp()
    app.mainloop()