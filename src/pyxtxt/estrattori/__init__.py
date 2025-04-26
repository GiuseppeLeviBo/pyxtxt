import os
import importlib

# Qui vengono registrati gli estrattori disponibili
estrattori = {}
pretty_names = {}

def register_extractor(mime_type, func, name=None):
    estrattori[mime_type] = func
    if name:
        pretty_names[mime_type] = name

# Carica automaticamente tutti i moduli presenti
current_dir = os.path.dirname(__file__)
for filename in os.listdir(current_dir):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{__name__}.{filename[:-3]}"
        importlib.import_module(module_name)
