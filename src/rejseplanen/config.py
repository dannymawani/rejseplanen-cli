"""Configuration management."""

import json
import os
from pathlib import Path

import keyring
from dotenv import load_dotenv

CONFIG_DIR = Path.home() / ".config" / "rejseplanen"
CONFIG_FILE = CONFIG_DIR / "config.json"


class Config:
    """Manages CLI configuration."""

    SERVICE_NAME = "rejseplanen-cli"

    def __init__(self):
        self.config_dir = CONFIG_DIR
        self.config_file = CONFIG_FILE
        self._ensure_config_dir()
        self._config = self._load_config()

        # Load .env file if it exists (from project root or cwd)
        load_dotenv()

    def _ensure_config_dir(self) -> None:
        """Create config directory if it doesn't exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        """Load configuration from file."""
        if not self.config_file.exists():
            return {}
        with open(self.config_file) as f:
            return json.load(f)

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self._config, f, indent=2)

    def get(self, key: str, default: str | None = None) -> str | None:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: str) -> None:
        """Set configuration value."""
        self._config[key] = value
        self._save_config()

    def get_api_key(self) -> str | None:
        """Get API key from multiple sources (priority order).

        Priority:
        1. Environment variable (REJSEPLANEN_API_KEY)
        2. .env file (loaded automatically)
        3. System keyring (secure storage)
        """
        # Try environment variable first (includes .env)
        api_key = os.getenv("REJSEPLANEN_API_KEY")
        if api_key:
            return api_key

        # Try keyring
        try:
            return keyring.get_password(self.SERVICE_NAME, "api_key")
        except Exception:
            return None

    def set_api_key(self, api_key: str) -> None:
        """Store API key in keyring."""
        try:
            keyring.set_password(self.SERVICE_NAME, "api_key", api_key)
        except Exception as e:
            raise RuntimeError(f"Failed to store API key: {e}")

    def get_saved_routes(self) -> dict:
        """Get saved routes."""
        return self._config.get("saved_routes", {})

    def save_route(self, name: str, origin: str, destination: str) -> None:
        """Save a route."""
        routes = self.get_saved_routes()
        routes[name] = {"origin": origin, "destination": destination}
        self._config["saved_routes"] = routes
        self._save_config()

    def delete_route(self, name: str) -> None:
        """Delete a saved route."""
        routes = self.get_saved_routes()
        if name in routes:
            del routes[name]
            self._config["saved_routes"] = routes
            self._save_config()
