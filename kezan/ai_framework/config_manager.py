"""Gestor de configuración para la IA."""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path
from ..config import API_CLIENT_ID, API_CLIENT_SECRET

class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.expanduser("~/.kezan/ai_config")
        self.config_path = Path(config_path)
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_path / "config.json"
        self.current_config = self._load_config()

    def _load_config(self) -> Dict:
        """Carga la configuración desde el archivo."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'api_credentials': {
                'client_id': API_CLIENT_ID,
                'client_secret': API_CLIENT_SECRET
            },
            'preferences': {
                'default_realm': '',
                'favorite_servers': [],
                'auto_analysis': True,
                'notification_threshold': 0.7  # Umbral de confianza para notificaciones
            },
            'ai_settings': {
                'analysis_interval': 300,  # segundos
                'pattern_detection_sensitivity': 0.5,
                'min_confidence_threshold': 0.6
            }
        }

    def save_config(self):
        """Guarda la configuración actual en el archivo."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.current_config, f, indent=2)

    def update_api_credentials(self, client_id: str, client_secret: str):
        """Actualiza las credenciales de la API."""
        self.current_config['api_credentials'].update({
            'client_id': client_id,
            'client_secret': client_secret
        })
        self.save_config()

    def update_preferences(self, **kwargs):
        """Actualiza las preferencias del usuario."""
        self.current_config['preferences'].update(kwargs)
        self.save_config()

    def update_ai_settings(self, **kwargs):
        """Actualiza la configuración de la IA."""
        self.current_config['ai_settings'].update(kwargs)
        self.save_config()

    def get_api_credentials(self) -> Dict[str, str]:
        """Obtiene las credenciales de la API."""
        return self.current_config['api_credentials']

    def get_preferences(self) -> Dict[str, Any]:
        """Obtiene las preferencias del usuario."""
        return self.current_config['preferences']

    def get_ai_settings(self) -> Dict[str, Any]:
        """Obtiene la configuración de la IA."""
        return self.current_config['ai_settings']

    def add_favorite_server(self, server: str):
        """Añade un servidor a la lista de favoritos."""
        if server not in self.current_config['preferences']['favorite_servers']:
            self.current_config['preferences']['favorite_servers'].append(server)
            self.save_config()

    def remove_favorite_server(self, server: str):
        """Elimina un servidor de la lista de favoritos."""
        if server in self.current_config['preferences']['favorite_servers']:
            self.current_config['preferences']['favorite_servers'].remove(server)
            self.save_config()

    def get_favorite_servers(self) -> list:
        """Obtiene la lista de servidores favoritos."""
        return self.current_config['preferences']['favorite_servers']
