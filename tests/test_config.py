import pytest
import config

class TestConfig:

    # --- CASOS FELICES (Happy Path) ---
    
    def test_config_constants_types(self):
        """Verifica que las constantes principales tengan el tipo de dato correcto."""
        assert isinstance(config.MODELO_VISION, str)
        assert isinstance(config.MODELOS_DISPONIBLES, list)
        assert isinstance(config.OLLAMA_URL, str)
        assert isinstance(config.CONFIG_CONSISTENTE, dict)
        assert isinstance(config.CATEGORIAS_POR_DEFECTO, list)

    def test_ollama_url_format(self):
        """Verifica que la URL de Ollama tenga un formato básico de endpoint."""
        assert config.OLLAMA_URL.startswith("http://")
        assert "/api/generate" in config.OLLAMA_URL

    def test_deterministic_settings(self):
        """Asegura que la configuración para evitar alucinaciones sea la correcta."""
        conf = config.CONFIG_CONSISTENTE
        assert conf['temperature'] == 0.0
        assert conf['seed'] == 42
        assert conf['stream'] is False


    # --- CASOS BORDE (Edge Cases) ---

    def test_modelos_disponibles_not_empty(self):
        """Verifica que al menos el modelo configurado por defecto esté en la lista de disponibles."""
        assert len(config.MODELOS_DISPONIBLES) > 0
        assert config.MODELO_VISION in config.MODELOS_DISPONIBLES

    def test_timeout_bounds(self):
        """Verifica que el timeout sea un valor razonable (ni muy bajo ni negativo)."""
        assert 30 <= config.TIMEOUT <= 300


    # --- CASOS DE ERROR / INTEGRIDAD ---

    def test_required_keys_in_config_dict(self):
        """Verifica que el diccionario de configuración no carezca de llaves críticas."""
        keys_requeridas = ['temperature', 'seed', 'num_predict', 'stream']
        for key in keys_requeridas:
            assert key in config.CONFIG_CONSISTENTE, f"Falta la llave crítica: {key}"

    def test_default_categories_integrity(self):
        """Verifica que la categoría 'desconocido' siempre exista para evitar fallos de clasificación."""
        assert 'desconocido' in config.CATEGORIAS_POR_DEFECTO

    def test_mocking_config_value(self, mocker):
        """Ejemplo de uso de pytest-mock para simular un cambio de modelo en tiempo de ejecución."""
        # Simulamos que el modelo cambia a uno experimental
        mocker.patch('config.MODELO_VISION', 'modelo-test-123')
        assert config.MODELO_VISION == 'modelo-test-123'