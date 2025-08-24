from .estrattori import estrattori
from functools import singledispatch
import io
import magic
from typing import Union, Optional
from urllib.parse import urlparse

@singledispatch
def xtxt(file_input):
    raise NotImplementedError(f"Type not supported : {type(file_input)}")

# Caso 1: file path (str)
@xtxt.register
def _(file_input: str) -> Optional[str]:
    try:
        with open(file_input, "rb") as f:
            data = f.read()
        buffer = io.BytesIO(data)
        buffer.name=file_input
        buffer.mimeType=magic.Magic(mime=True).from_file(file_input)
        return xtxt(buffer)
    except Exception as e:
        print(f"⚠️ File opening error'{file_input}': {e}")
        return None

# Caso 2: buffer (BytesIO)
@xtxt.register
def _(file_input: io.BytesIO) -> Optional[str]:
    try:


        # Mappa dei MIME Type gestiti dagli estrattori
        # estrattori = {
            # "application/pdf": xtxt_pdf,
            # "application/vnd.openxmlformats-officedocument.wordprocessingml.document": xtxt_docx,
            # "application/vnd.openxmlformats-officedocument.presentationml.presentation": xtxt_pptx,
            # "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": xtxt_xlsx,
            # "application/vnd.ms-excel": xtxt_xls,
            # "text/plain": xtxt_txt,
            # "application/vnd.oasis.opendocument.text": xtxt_odt,
            # "text/html": xtxt_html,
# #            "text/rtf": xtxt_rtf,
            # "application/xml": xtxt_xml,
            # "text/xml": xtxt_xml,
        # }
        if hasattr(file_input,'mimeType'):
            mime_type=file_input.mimeType
        else:
            mime_type = magic.Magic(mime=True).from_buffer(file_input.read(2048))
            file_input.name='IO_buffer'
            file_input.seek(0)
        if mime_type.startswith("text/"):
            if (mime_type != "text/html") and (mime_type != "text/xml") and (mime_type != "text/plain"):
               print(f"📄 File recognized as text type: {mime_type}, treated as text/plain")
               mime_type = "text/plain"
        if mime_type not in estrattori:
            print(f"⚠️ MIME type not supported {mime_type} ({file_input.name}) ignored.")
            return None


        # Estrai il testo
        testo = estrattori[mime_type](file_input)
        return f"{testo}"
    except  Exception as e:
        print(f"❌ Error while reading: {e}")
        return None

# Caso 3: bytes object
@xtxt.register
def _(file_input: bytes) -> Optional[str]:
    """Estrae testo da oggetto bytes (es. da download web)"""
    try:
        buffer = io.BytesIO(file_input)
        buffer.name = 'bytes_input'
        mime_type = magic.Magic(mime=True).from_buffer(file_input[:2048])
        buffer.mimeType = mime_type
        return xtxt(buffer)
    except Exception as e:
        print(f"❌ Error processing bytes: {e}")
        return None

# Supporto per requests.Response (se disponibile)
try:
    import requests
    
    @xtxt.register
    def _(file_input: requests.Response) -> Optional[str]:
        """Estrae testo da requests.Response object"""
        try:
            return xtxt(file_input.content)
        except Exception as e:
            print(f"❌ Error processing Response: {e}")
            return None
except ImportError:
    # requests non installato, skip registrazione
    pass

def xtxt_from_url(url: str, **kwargs) -> Optional[str]:
    """Scarica contenuto da URL e ne estrae il testo
    
    Args:
        url: URL del documento da processare  
        **kwargs: Parametri aggiuntivi per requests.get()
        
    Returns:
        str: Testo estratto o None se errore
    """
    try:
        import requests
        response = requests.get(url, **kwargs)
        response.raise_for_status()
        return xtxt(response.content)
    except ImportError:
        print("❌ requests library not installed. Install with: pip install requests")
        return None
    except Exception as e:
        print(f"❌ Error downloading from URL {url}: {e}")
        return None

def extxt_available_formats(pretty=False):
    if pretty:
        from .estrattori import pretty_names
        return sorted({pretty_names.get(mime, mime) for mime in estrattori.keys()})
    else:
        return sorted(estrattori.keys())