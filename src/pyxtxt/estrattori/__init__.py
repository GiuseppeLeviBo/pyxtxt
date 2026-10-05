import os
import importlib
import warnings

# Qui vengono registrati gli estrattori disponibili
estrattori = {}
pretty_names = {}

def register_extractor(mime_type, func, name=None):
    estrattori[mime_type] = func
    if name:
        pretty_names[mime_type] = name

# Carica automaticamente tutti i moduli presenti.
# L'ordine alfabetico rende deterministico chi vince quando due moduli registrano
# lo stesso MIME type: l'ultimo caricato sovrascrive (es. ocr_ollama sovrascrive ocr).
# Un modulo difettoso non deve impedire l'import dell'intero pacchetto.
current_dir = os.path.dirname(__file__)
for filename in sorted(os.listdir(current_dir)):
    if filename.endswith(".py") and filename != "__init__.py":
        module_name = f"{__name__}.{filename[:-3]}"
        try:
            importlib.import_module(module_name)
        except Exception as e:
            warnings.warn(f"pyxtxt: extractor module '{module_name}' could not be loaded: {e}")
