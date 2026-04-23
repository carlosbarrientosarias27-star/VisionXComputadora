import sys
import os
# Añade la carpeta superior (raíz) al camino de búsqueda de Python
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import json
import requests
from app_1 import clasificar_imagen_local

## --- FIXTURES PARA MOCKEAR CONFIG ---
@pytest.fixture(autouse=True)
def setup_mocks(mocker):
    # Parchar las constantes directamente en el espacio de nombres de app_1
    mocker.patch("app_1.MODELO_VISION", "llava:7b")
    mocker.patch("app_1.OLLAMA_URL", "http://fake-url/api/generate")
    mocker.patch("app_1.TIMEOUT", 5)
    mocker.patch("app_1.CONFIG_CONSISTENTE", {"temperature": 0})
    
    # Parchar requests.post de forma general para evitar llamadas reales accidentales
    return mocker.patch("requests.post")

## --- CASO 1: CASO FELIZ (HAPPY PATH) ---
def test_clasificar_imagen_exito(mocker, setup_mocks):
    mock_post = setup_mocks
    
    # 1. Parchar la apertura de archivos SOLO para app_1
    # Esto evita romper el 'open' general de Python
    mocker.patch("app_1.open", mocker.mock_open(read_data=b"fake_binary_data"))
    
    # 2. Configurar la respuesta
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": json.dumps({
            "categoria": "naturaleza",
            "confianza": 0.98,
            "razones": "Se ve un bosque"
        })
    }
    mock_post.return_value = mock_response

    resultado = clasificar_imagen_local("foto.jpg", ["naturaleza"])

    assert resultado["categoria"] == "naturaleza"
    assert resultado["confianza"] == 0.98

## --- CASO 2: CASOS DE BORDE (EDGE CASES) ---
def test_clasificar_imagen_json_invalido(mocker):
    """
    El modelo responde pero el contenido no es un JSON válido (típico de LLMs).
    """
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    # El modelo devuelve texto plano en lugar de un string JSON
    mock_response.json.return_value = {"response": "Lo siento, no puedo procesar esto."}
    mocker.patch("requests.post", return_value=mock_response)

    resultado = clasificar_imagen_local("foto.jpg", ["cat1"])

    # La función debería caer en el bloque 'except' al hacer json.loads()
    assert resultado["categoria"] == "error"
    assert "Error" in resultado["razones"]

def test_clasificar_imagen_vacia_o_desconocida(mocker):
    """
    El modelo responde correctamente pero indica que no conoce la categoría.
    """
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "response": '{"categoria": "desconocido", "confianza": 0.0, "razones": "No se reconoce nada"}'
    }
    mocker.patch("requests.post", return_value=mock_response)

    resultado = clasificar_imagen_local("foto.jpg", ["naturaleza"])
    assert resultado["categoria"] == "desconocido"

## --- CASO 3: CASOS DE ERROR (ERROR HANDLING) ---
def test_clasificar_imagen_error_red(mocker):
    """
    Simula un error de conexión o timeout en la API.
    """
    mocker.patch("builtins.open", mocker.mock_open(read_data=b"data"))
    
    # Simulamos que requests lanza una excepción
    mocker.patch("requests.post", side_effect=requests.exceptions.ConnectionError("Fallo de red"))

    resultado = clasificar_imagen_local("foto.jpg", ["cat1"])

    assert resultado["categoria"] == "error"
    assert "Fallo de red" in resultado["razones"]

def test_clasificar_imagen_archivo_no_encontrado(mocker):
    """
    Simula que el archivo de imagen no existe en el disco.
    """
    mocker.patch("builtins.open", side_effect=FileNotFoundError("Archivo no encontrado"))

    resultado = clasificar_imagen_local("ruta/falsa.jpg", ["cat1"])

    assert resultado["categoria"] == "error"
    assert "Archivo no encontrado" in resultado["razones"]