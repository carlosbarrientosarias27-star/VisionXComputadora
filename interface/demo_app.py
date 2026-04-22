import os
import sys 
import threading
import base64
import requests
import json
import customtkinter as ctk
from PIL import Image

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

# Configuración de apariencia
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class VisionXApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("VisionXComputadora - Clasificador")
        self.geometry("1150x750")
        self.configure(fg_color="#181818")

        self.imagenes_seleccionadas = [] # Estado de las imágenes

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

    # --- TUS FUNCIONES DE LÓGICA INTEGRADAS ---
    def setup_logic(self):
        self.add_btn.configure(command=self.agregar_categoria_manual)
        self.select_btn.configure(command=self.seleccionar_imagenes)
        self.clear_btn.configure(command=self.limpiar_imagenes)
        self.classify_btn.configure(command=self.iniciar_clasificacion)

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

    def seleccionar_imagenes(self):
        files = ctk.filedialog.askopenfilenames(title="Seleccionar imágenes",
                                                filetypes=[("Imágenes", "*.jpg *.jpeg *.png *.webp")])
        if files:
            self.imagenes_seleccionadas = list(files)
            self.drop_lbl.configure(text=f"✅ {len(files)} imágenes seleccionadas", text_color="#4cd137")

    def limpiar_imagenes(self):
        self.imagenes_seleccionadas = []
        self.drop_lbl.configure(text="No hay imágenes seleccionadas", text_color="#7f8c8d")

    def iniciar_clasificacion(self):

        self.result_area.delete("0.0", "end")

        """Función que se ejecuta al pulsar el botón 🚀 CLASIFICAR"""
        if not self.imagenes_seleccionadas:
            # Si no hay imágenes, avisamos en el cuadro de resultados
            self.result_area.insert("0.0", "❌ ERROR: No has seleccionado ninguna imagen.\n")
            self.result_area.insert("end", "Haz clic en '📁 Seleccionar' primero.")
            return

        # Si hay imágenes, mostramos un mensaje de carga
        self.result_area.insert("0.0", "🚀 INICIANDO PROCESO...\n")
        self.result_area.insert("end", f"----------------------------\n")
        self.result_area.insert("end", f"📸 Imágenes detectadas: {len(self.imagenes_seleccionadas)}\n")
        self.result_area.insert("end", f"🏷 Categorías: {self.cat_display.get('0.0', 'end').strip()}\n")
        self.result_area.insert("end", f"----------------------------\n")
        self.result_area.insert("end", "⏳ Conectando con Ollama (esto puede tardar)...")
        # Aquí es donde más adelante pondremos la lógica para llamar a la IA
        print("Botón pulsado con éxito") 

    def ejecutar_peticion_ollama(self):
        try:
            # Usamos la primera imagen seleccionada
            ruta_imagen = self.imagenes_seleccionadas[0]
            
            # 1. Convertir imagen a Base64 (Fundamental para que Ollama la vea)
            with open(ruta_imagen, "rb") as f:
                img_base64 = base64.b64encode(f.read()).decode('utf-8')

            # 2. Configurar el envío
            categorias = self.cat_display.get("0.0", "end").strip()
            payload = {
                "model": "llava", # Forzamos llava que es el que tiene visión
                "prompt": f"Clasifica esta imagen en una de estas categorías: {categorias}. Responde: CATEGORIA, CONFIANZA y RAZONES.",
                "images": [img_base64],
                "stream": False
            }

            # 3. Petición a Ollama
            respuesta = requests.post(config.OLLAMA_URL, json=payload, timeout=config.TIMEOUT)
            
            # 4. Mostrar resultado en TU result_area (Limpiando lo anterior)
            self.result_area.delete("0.0", "end")
            if respuesta.status_code == 200:
                final = respuesta.json().get("response", "Sin respuesta")
                self.result_area.insert("end", f"✅ ANALISIS COMPLETADO:\n\n{final}")
            else:
                self.result_area.insert("end", f"❌ Error de Ollama: {respuesta.status_code}\nRevisa que el modelo 'llava' esté descargado.")

        except Exception as e:
            self.result_area.delete("0.0", "end")
            self.result_area.insert("end", f"❌ Error crítico: {str(e)}")
        
        self.result_area.see("end")

if __name__ == "__main__":
    app = VisionXApp()
    app.mainloop()