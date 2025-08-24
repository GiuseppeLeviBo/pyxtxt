from .core import xtxt, extxt_available_formats, xtxt_from_url

# Import EXIF functions if available
try:
    from .estrattori.exif import xtxt_image_exif
    exif_available = True
except ImportError:
    exif_available = False

# Import OCR-Ollama functions if available
try:
    from .estrattori.ocr_ollama import (
        set_ollama_model, get_ollama_model, xtxt_image_describe,
        set_ollama_config, get_ollama_config, reset_ollama_config,
        xtxt_image_with_confidence, configure_for_medical_images,
        configure_for_xray_images, quick_xray_analysis
    )
    ollama_available = True
except ImportError:
    ollama_available = False

# Build __all__ dynamically based on available features
__all__ = ["xtxt", "extxt_available_formats", "xtxt_from_url"]

if exif_available:
    __all__.extend(["xtxt_exif"])

if ollama_available:
    __all__.extend([
        "set_ollama_model", "get_ollama_model", "xtxt_image_describe",
        "set_ollama_config", "get_ollama_config", "reset_ollama_config",
        "xtxt_image_with_confidence", "configure_for_medical_images",
        "configure_for_xray_images", "quick_xray_analysis"
    ])

# Define EXIF wrapper function
def xtxt_exif(file_input):
    """
    Extract EXIF metadata from image files.
    
    Args:
        file_input: Image file path (str) or file-like object
        
    Returns:
        str: Formatted EXIF metadata or empty string if no EXIF data
        
    Example:
        exif_data = xtxt_exif("photo.jpg")
        print(exif_data)
    """
    if not exif_available:
        raise ImportError("EXIF extraction requires Pillow. Install with: pip install pyxtxt[ocr]")
    
    # Handle file path
    if isinstance(file_input, str):
        with open(file_input, 'rb') as f:
            return xtxt_image_exif(f)
    else:
        return xtxt_image_exif(file_input)
