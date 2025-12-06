"""Tests for configuration module."""

from unittest.mock import patch

from rejseplanen.config import Config


def test_config_initialization():
    """Test config initialization."""
    with patch('pathlib.Path.mkdir'):
        with patch('rejseplanen.config.Config._load_config', return_value={}):
            config = Config()
            assert config is not None


def test_get_api_key_from_env():
    """Test getting API key from environment."""
    with patch('pathlib.Path.mkdir'):
        with patch('rejseplanen.config.Config._load_config', return_value={}):
            with patch('os.environ.get', return_value='env_key'):
                config = Config()
                key = config.get_api_key()
                assert key == 'env_key'


def test_save_and_get_route():
    """Test saving and retrieving routes."""
    with patch('pathlib.Path.mkdir'):
        with patch('rejseplanen.config.Config._load_config', return_value={'routes': {}}):
            with patch('rejseplanen.config.Config._save_config'):
                config = Config()

                # Save a route
                config.save_route("test-route", "Origin", "Destination")

                # Get saved routes
                routes = config.get_saved_routes()
                assert "test-route" in routes
                assert routes["test-route"]["origin"] == "Origin"
                assert routes["test-route"]["destination"] == "Destination"


def test_delete_route():
    """Test deleting a route."""
    with patch('pathlib.Path.mkdir'):
        initial_config = {
            'routes': {
                'test-route': {'origin': 'A', 'destination': 'B'}
            }
        }
        with patch('rejseplanen.config.Config._load_config', return_value=initial_config):
            with patch('rejseplanen.config.Config._save_config'):
                config = Config()

                # Delete route
                config.delete_route("test-route")

                # Verify it's gone
                routes = config.get_saved_routes()
                assert "test-route" not in routes


def test_delete_nonexistent_route():
    """Test deleting a route that doesn't exist."""
    with patch('pathlib.Path.mkdir'):
        with patch('rejseplanen.config.Config._load_config', return_value={'routes': {}}):
            config = Config()

            # Should not raise error
            config.delete_route("nonexistent")
            routes = config.get_saved_routes()
            assert "nonexistent" not in routes

