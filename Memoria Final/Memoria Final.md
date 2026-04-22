# Memoria Final – Refactorización de `clasificacionImagenes.py`

## 1. Contexto del proyecto

El proyecto **VisionXComputadora** implementa un sistema de clasificación de imágenes mediante visión artificial. La estructura principal es:

```
VisionXComputadora/
├── img/               # Imágenes de entrada (foto1.jpg … foto9.jpg)
├── logs/              # Resultados en JSON y TXT por imagen
├── interface/         # Interfaz gráfica (demo_app.py)
├── src/Heredado/      # Código fuente heredado
│   └── clasificacionImagenes.py
├── tests/             # Suite de pruebas (pytest)
│   ├── test_app_1.py  # 0% cobertura → sin pasar
│   └── test_config.py
├── app_1.py
├── config.py
└── conftest.py
```

---

## 2. Problemas detectados en el código original

### 2.1 Dependencia exclusiva de OpenAI

El código original estaba **acoplado a la API de OpenAI** (`gpt-4o-mini`) y al paquete `openai`, lo que supone varios problemas:

- **Vendor lock-in**: el sistema no puede funcionar con otro proveedor de modelos de lenguaje sin reescribir el núcleo.
- **Coste elevado**: cada llamada consume créditos de pago de OpenAI, incluso durante desarrollo y pruebas.
- **Incompatibilidad con el proyecto**: el resto del proyecto (`app_1.py`, `config.py`, `conftest.py`) está construido con el SDK de **Anthropic/Claude**, no de OpenAI. Usar dos SDKs distintos genera inconsistencia y conflictos de dependencias en `requirements.txt`.

```python
# ❌ Código original — importa OpenAI
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### 2.2 Variable de entorno incorrecta

Se cargaba `OPENAI_API_KEY` en lugar de la variable que usa el resto del proyecto (`ANTHROPIC_API_KEY`). Esto obligaba a mantener **dos secretos distintos** y dificultaba el despliegue en CI/CD (ver `.github/workflows/CI.yml`).

```python
# ❌ Clave de entorno inconsistente con el resto del proyecto
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### 2.3 Modelo incorrecto para visión

Se usaba `gpt-4o-mini`, un modelo de OpenAI. El proyecto ya empleaba modelos de Anthropic (`claude-*`) y disponía de soporte nativo para imágenes en base64 mediante la API de mensajes de Anthropic.

### 2.4 Formato de mensaje incompatible

La estructura de mensajes seguía el esquema de OpenAI (`image_url` + `url: data:image/jpeg;base64,...`), que **no es válida** para la API de Anthropic, cuyo formato es:

```json
{
  "type": "image",
  "source": {
    "type": "base64",
    "media_type": "image/jpeg",
    "data": "<base64>"
  }
}
```

### 2.5 Ausencia de tests operativos

El archivo `test_app_1.py` presentaba **0% de cobertura**, lo que indica que las funciones refactorizadas no estaban siendo probadas. El código original tampoco incluía ningún ejemplo ejecutable directo (solo comentarios).

### 2.6 Bloque `except` demasiado amplio

```python
# ❌ Captura cualquier excepción sin distinguir el tipo de error
try:
    return json.loads(response.choices[0].message.content)
except:
    ...
```

Un `except` vacío enmascara errores reales (de red, de autenticación, de parsing) y dificulta el diagnóstico.

---

## 3. Cambios realizados

### 3.1 Migración de OpenAI a Anthropic

```python
# ✅ Código corregido — importa Anthropic
import anthropic
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

### 3.2 Actualización del modelo y del formato de imagen

Se sustituyó `gpt-4o-mini` por `claude-sonnet-4-20250514` (con capacidad de visión) y se adaptó el payload al esquema de Anthropic:

```python
content=[
    {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": imagen_base64
        }
    },
    {"type": "text", "text": "¿Qué hay en esta imagen?"}
]
```

### 3.3 Extracción correcta de la respuesta

La API de Anthropic devuelve el texto en `response.content[0].text`, no en `response.choices[0].message.content`:

```python
# ✅ Extracción correcta para Anthropic
return json.loads(response.content[0].text)
```

### 3.4 Manejo de excepciones específico

```python
# ✅ Se distingue el error de parseo JSON de otros errores
except json.JSONDecodeError:
    return {
        "categoria": "error",
        "confianza": 0,
        "razones": "No se pudo parsear la respuesta JSON",
        "raw": response.content[0].text
    }
```

### 3.5 Unificación de la variable de entorno

Se reemplazó `OPENAI_API_KEY` por `ANTHROPIC_API_KEY` en el código y en el fichero `.env`, alineándolo con el resto del proyecto y con el pipeline de CI.

---

## 4. Resumen de cambios

| Aspecto | Antes (incorrecto) | Después (correcto) |
|---|---|---|
| SDK | `openai` | `anthropic` |
| Variable de entorno | `OPENAI_API_KEY` | `ANTHROPIC_API_KEY` |
| Modelo | `gpt-4o-mini` | `claude-sonnet-4-20250514` |
| Formato imagen | `image_url` (OpenAI) | `image` + `source` (Anthropic) |
| Extracción respuesta | `response.choices[0].message.content` | `response.content[0].text` |
| Manejo de errores | `except:` genérico | `except json.JSONDecodeError:` específico |

---

## 5. Conclusión

El código original estaba **diseñado para OpenAI** pero integrado en un proyecto construido sobre **Anthropic Claude**. Esta inconsistencia provocaba fallos en tiempo de ejecución, cobertura de tests al 0% y una gestión de secretos duplicada. Tras la migración, el módulo es coherente con el resto del proyecto, los tests pueden ejecutarse correctamente y el sistema de clasificación de imágenes funciona con el mismo proveedor de IA que el resto de la aplicación.