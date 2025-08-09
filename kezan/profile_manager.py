from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, List
import json
import os
from pathlib import Path

class GameVersion(Enum):
    RETAIL = "retail"
    CLASSIC = "classic"
    CLASSIC_ERA = "classic_era"

@dataclass
class SearchPreferences:
    default_realm: str
    watched_items: List[int]
    price_thresholds: Dict[int, int]  # item_id: max_price
    notification_enabled: bool

@dataclass
class Profile:
    version: GameVersion
    preferences: SearchPreferences
    last_scan: Optional[str] = None
    auction_history: Dict[int, List[dict]] = None

class ProfileManager:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = os.path.expanduser("~/.kezan/profiles")
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.active_profile: Optional[Profile] = None
        self._load_or_create_profiles()

    def _load_or_create_profiles(self):
        """Inicializa perfiles por defecto si no existen."""
        for version in GameVersion:
            profile_path = self.config_dir / f"{version.value}.json"
            if not profile_path.exists():
                default_prefs = SearchPreferences(
                    default_realm="",
                    watched_items=[],
                    price_thresholds={},
                    notification_enabled=True
                )
                profile = Profile(
                    version=version,
                    preferences=default_prefs,
                    auction_history={}
                )
                self.save_profile(profile)

    def get_profile(self, version: GameVersion) -> Profile:
        """Obtiene un perfil específico."""
        profile_path = self.config_dir / f"{version.value}.json"
        if not profile_path.exists():
            raise ValueError(f"No existe perfil para {version.value}")
        
        with open(profile_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            prefs = SearchPreferences(**data['preferences'])
            return Profile(
                version=version,
                preferences=prefs,
                last_scan=data.get('last_scan'),
                auction_history=data.get('auction_history', {})
            )

    def save_profile(self, profile: Profile):
        """Guarda un perfil en disco."""
        profile_path = self.config_dir / f"{profile.version.value}.json"
        data = {
            'version': profile.version.value,
            'preferences': {
                'default_realm': profile.preferences.default_realm,
                'watched_items': profile.preferences.watched_items,
                'price_thresholds': profile.preferences.price_thresholds,
                'notification_enabled': profile.preferences.notification_enabled
            },
            'last_scan': profile.last_scan,
            'auction_history': profile.auction_history
        }
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def set_active_profile(self, version: GameVersion):
        """Establece el perfil activo."""
        self.active_profile = self.get_profile(version)

    def update_preferences(self, version: GameVersion, **kwargs):
        """Actualiza las preferencias de un perfil específico."""
        profile = self.get_profile(version)
        for key, value in kwargs.items():
            if hasattr(profile.preferences, key):
                setattr(profile.preferences, key, value)
        self.save_profile(profile)

    def add_watched_item(self, version: GameVersion, item_id: int, max_price: Optional[int] = None):
        """Añade un item a la lista de observados."""
        profile = self.get_profile(version)
        if item_id not in profile.preferences.watched_items:
            profile.preferences.watched_items.append(item_id)
            if max_price is not None:
                profile.preferences.price_thresholds[item_id] = max_price
            self.save_profile(profile)

    def remove_watched_item(self, version: GameVersion, item_id: int):
        """Elimina un item de la lista de observados."""
        profile = self.get_profile(version)
        if item_id in profile.preferences.watched_items:
            profile.preferences.watched_items.remove(item_id)
            profile.preferences.price_thresholds.pop(item_id, None)
            self.save_profile(profile)

    def update_auction_history(self, version: GameVersion, item_id: int, auction_data: dict):
        """Actualiza el historial de subastas para un item."""
        profile = self.get_profile(version)
        if profile.auction_history is None:
            profile.auction_history = {}
        
        if item_id not in profile.auction_history:
            profile.auction_history[item_id] = []
        
        profile.auction_history[item_id].append(auction_data)
        # Mantener solo los últimos 100 registros por item
        if len(profile.auction_history[item_id]) > 100:
            profile.auction_history[item_id] = profile.auction_history[item_id][-100:]
        
        self.save_profile(profile)
