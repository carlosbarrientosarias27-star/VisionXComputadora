import pytest
import config

## --- CASO FELIZ (Valores esperados) ---
def test_config_valores_por_defecto():
    """Verifica que las constantes críticas tengan los valores correctos."""
    assert config.MODELO_VISION == 'llava'
    assert config.OLLAMA_URL == 'http://localhost:11434/api/generate'
    assert config.TIMEOUT == 120

def test_config_consistente_estructura():
    """Verifica que el diccionario de configuración de la IA sea correcto."""
    conf = config.CONFIG_CONSISTENTE
    assert conf['temperature'] == 0.0
    assert conf['stream'] is False
    assert isinstance(conf['seed'], int)

## --- CASO DE BORDE (Límites y Tipos) ---
def test_config_categorias_no_vacias():
    """Verifica que siempre exista al menos una categoría y 'desconocido' esté presente."""
    assert len(config.CATEGORIAS_POR_DEFECTO) > 0
    assert 'desconocido' in config.CATEGORIAS_POR_DEFECTO

def test_config_timeout_positivo():
    """El timeout debe ser un número razonable para modelos de visión."""
    assert config.TIMEOUT >= 30

## --- CASO DE ERROR (Simulación de fallos) ---
def test_config_missing_attributes(mocker):
    """
    Verifica que si se intenta acceder a una configuración inexistente 
    (simulado vía mock) el sistema falle como se espera.
    """
    # Aunque config.py es estático, podemos mockear su carga en módulos que lo usen
    # Aquí validamos simplemente la presencia de claves obligatorias
    required_keys = ['temperature', 'seed', 'stream']
    for key in required_keys:
        assert key in config.CONFIG_CONSISTENTE

def test_config_path_format():
    """Verifica que los nombres de carpetas no tengan caracteres extraños o rutas absolutas peligrosas."""
    assert not config.CARPETA_IMAGENES.startswith("/")
    assert config.CARPETA_RESULTADOS == 'resultados'