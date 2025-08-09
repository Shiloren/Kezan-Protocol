import pytest
import os
import tempfile
from pathlib import Path
from kezan.profile_manager import ProfileManager, GameVersion, Profile, SearchPreferences

@pytest.fixture
def temp_config_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def profile_manager(temp_config_dir):
    return ProfileManager(config_dir=temp_config_dir)

def test_profile_creation(profile_manager):
    """Verifica que los perfiles se crean correctamente."""
    # Verificar que se han creado todos los perfiles por defecto
    for version in GameVersion:
        profile = profile_manager.get_profile(version)
        assert profile.version == version
        assert isinstance(profile.preferences, SearchPreferences)
        assert profile.preferences.watched_items == []

def test_save_and_load_profile(profile_manager):
    """Verifica que los perfiles se guardan y cargan correctamente."""
    # Modificar un perfil
    profile_manager.update_preferences(
        GameVersion.RETAIL,
        default_realm="Sargeras",
        watched_items=[19019, 13422]
    )
    
    # Cargar el perfil y verificar cambios
    profile = profile_manager.get_profile(GameVersion.RETAIL)
    assert profile.preferences.default_realm == "Sargeras"
    assert profile.preferences.watched_items == [19019, 13422]

def test_watched_items_management(profile_manager):
    """Verifica la gestión de items observados."""
    version = GameVersion.CLASSIC
    
    # Añadir items
    profile_manager.add_watched_item(version, 19019, 50000)  # Thunderfury
    profile_manager.add_watched_item(version, 13422)  # Stoneshield Potion
    
    # Verificar items
    profile = profile_manager.get_profile(version)
    assert 19019 in profile.preferences.watched_items
    assert 13422 in profile.preferences.watched_items
    assert profile.preferences.price_thresholds[19019] == 50000
    
    # Eliminar item
    profile_manager.remove_watched_item(version, 19019)
    profile = profile_manager.get_profile(version)
    assert 19019 not in profile.preferences.watched_items
    assert 19019 not in profile.preferences.price_thresholds

def test_auction_history(profile_manager):
    """Verifica el manejo del historial de subastas."""
    version = GameVersion.RETAIL
    item_id = 19019
    
    # Añadir datos de subasta
    auction_data = {
        "price": 500000,
        "timestamp": "2025-08-09T12:00:00Z",
        "quantity": 1
    }
    
    profile_manager.update_auction_history(version, item_id, auction_data)
    
    # Verificar datos
    profile = profile_manager.get_profile(version)
    assert item_id in profile.auction_history
    assert len(profile.auction_history[item_id]) == 1
    assert profile.auction_history[item_id][0] == auction_data

def test_multiple_versions(profile_manager):
    """Verifica que los perfiles de diferentes versiones son independientes."""
    # Configurar perfiles diferentes
    profile_manager.update_preferences(
        GameVersion.RETAIL,
        default_realm="Sargeras",
        watched_items=[19019]
    )
    
    profile_manager.update_preferences(
        GameVersion.CLASSIC,
        default_realm="Faerlina",
        watched_items=[13422]
    )
    
    # Verificar que son independientes
    retail = profile_manager.get_profile(GameVersion.RETAIL)
    classic = profile_manager.get_profile(GameVersion.CLASSIC)
    
    assert retail.preferences.default_realm == "Sargeras"
    assert classic.preferences.default_realm == "Faerlina"
    assert retail.preferences.watched_items != classic.preferences.watched_items
