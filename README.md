# 🖥️ VisionXComputadora

Sistema de clasificación de imágenes basado en visión por computadora, con interfaz de demostración, pipeline de logs estructurados y suite de tests automatizados.

---

## 📁 Estructura del Proyecto

```
VisionXComputadora/
├── .github/
│   └── workflows/
│       └── CI.yml                    # Pipeline de integración continua
├── docs/                             # Documentación del proyecto
├── img/                              # Imágenes de entrada
│   ├── foto1.jpg
│   ├── foto2.jpg
│   └── ... (foto1–foto9)
├── interface/
│   ├── demo_app.py                   # Aplicación de demostración principal
│   └── demo1.py                      # Script de demostración auxiliar
├── logs/                             # Registros de inferencia por imagen
│   ├── foto1.json / foto1.txt
│   ├── foto2.json / foto2.txt
│   └── ... (foto1–foto9)
├── Memoria Final/                    # Documentación y memoria final del proyecto
├── proceso_20*/                      # Carpeta de proceso con resultados por ejecución
│   ├── json/                         # Resultados estructurados en formato JSON
│   │   ├── .gitkeep
│   │   ├── foto1.json
│   │   ├── foto2.json
│   │   └── ... (foto1–foto9)
│   ├── txt/                          # Resúmenes legibles en formato TXT
│   │   ├── .gitkeep
│   │   ├── foto1.txt
│   │   ├── foto2.txt
│   │   └── ... (foto1–foto9)
│   ├── .gitkeep
│   └── clasificacion*.json           # Archivo resumen de la clasificación del proceso
├── resultados/                       # Resultados consolidados del sistema
├── src/
│   └── Heredado/
│       ├── __init__.py
│       └── clasificacionImagenes.py  # Lógica principal de clasificación
├── tests/
│   ├── __pycache__/
│   ├── __init__.py
│   ├── test_app_1.py
│   └── test_config.py
├── app_1.py                          # Punto de entrada principal
├── config.py                         # Configuración global
├── conftest.py                       # Fixtures de pytest
├── .coverage                         # Reporte de cobertura de tests
├── .env                              # Variables de entorno (no versionado)
├── .gitignore
├── LICENSE
├── pytest.ini                        # Configuración de pytest
├── requirements.txt                  # Dependencias del proyecto
└── README.md
```

---

## 🚀 Instalación

### Requisitos previos

- Python 3.10+ o superior
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/VisionXComputadora.git
cd VisionXComputadora

# 2. Crear y activar entorno virtual
python -m venv .env
source .env/bin/activate        # Linux/macOS
.env\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores
```

---

## ⚙️ Uso

### Ejecutar la aplicación principal

```bash
python app_1.py
```

### Ejecutar la interfaz de demostración

```bash
python interface/demo_app.py
```

### Clasificar imágenes manualmente

Las imágenes deben ubicarse en el directorio `img/`. Los resultados se generan automáticamente en `logs/` en formato `.json` y `.txt`.

---

## 🧪 Tests

```bash
# Ejecutar todos los tests
pytest

# Ejecutar con reporte de cobertura
pytest --cov=src --cov-report=term-missing

# Ejecutar un test específico
pytest tests/test_app_1.py
```

### Cobertura actual

| Módulo              | Cobertura |
|---------------------|-----------|
| `config.py`         | 100%      |
| `conftest.py`       | 100%      |
| `tests/__init__.py` | 100%      |
| `test_config.py`    | 100%      |
| `app_1.py`          | 0% ⚠️     |
| `test_app_1.py`     | 0% ⚠️     |
| **tests (global)**  | ~32%      |

> ⚠️ Se recomienda incrementar la cobertura de `app_1.py` y `test_app_1.py`.

---

## 🔄 CI/CD

El proyecto incluye un workflow de GitHub Actions (`.github/workflows/CI.yml`) que ejecuta automáticamente los tests en cada push o pull request a la rama principal.

---

## 📊 Logs

Por cada imagen procesada se generan dos archivos en `logs/`:

- **`fotoN.json`** — Resultado estructurado de la clasificación (etiquetas, confianza, metadatos).
- **`fotoN.txt`** — Resumen legible del resultado.

---

## 🧩 Módulos principales

### `src/Heredado/clasificacionImagenes.py`
Contiene la lógica central de clasificación de imágenes. Hereda o extiende funcionalidades base del sistema de visión.

### `config.py`
Gestiona la configuración global del sistema (rutas, parámetros del modelo, umbrales, etc.).

### `app_1.py`
Punto de entrada principal. Orquesta la carga de imágenes, clasificación y escritura de logs.

### `interface/demo_app.py`
Interfaz de demostración interactiva para visualizar resultados de clasificación en tiempo real.

---

## 📄 Licencia

Este proyecto está bajo la licencia especificada en el archivo [LICENSE](LICENSE).

---

## 🤝 Contribuciones

1. Haz un fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Realiza tus cambios y añade tests
4. Asegúrate de que todos los tests pasen (`pytest`)
5. Abre un Pull Request

---