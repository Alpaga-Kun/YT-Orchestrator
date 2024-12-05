import os
import importlib
from pathlib import Path
from .base_soundprovider import BaseSoundProvider

sound_providers = {}

def load_providers(directory):
    base_dir = Path(directory)
    for item in os.listdir(base_dir):
        item_path = base_dir / item
        if item_path.is_dir() and not item.startswith('__'):
            load_providers(item_path)  # Recherche récursive
        elif item.endswith('.py') and item != '__init__.py':
            module_name = item_path.stem
            module_path = f".{module_name}"
            module = importlib.import_module(module_path, package="srcs.providers")

            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, BaseSoundProvider) and attr is not BaseSoundProvider:
                    if hasattr(attr, 'provider_name') and attr.provider_name:
                        sound_providers[attr.provider_name.lower()] = attr

# Charger les fournisseurs au démarrage
load_providers(Path(__file__).parent / "providers")
