from functools import singledispatch
import io
from typing import Optional

import magic

from .estrattori import estrattori


@singledispatch
def xtxt(file_input):
    raise NotImplementedError(f"Type not supported : {type(file_input)}")


@xtxt.register
def _(file_input: str) -> Optional[str]:
    """Extract text from a file path."""
    try:
        with open(file_input, "rb") as f:
            data = f.read()
        buffer = io.BytesIO(data)
        buffer.name = file_input
        buffer.mimeType = magic.Magic(mime=True).from_file(file_input)
        return xtxt(buffer)
    except Exception as e:
        print(f"⚠️ File opening error '{file_input}': {e}")
        return None


@xtxt.register
def _(file_input: io.BytesIO) -> Optional[str]:
    """Extract text from a BytesIO buffer."""
    try:
        if hasattr(file_input, "mimeType"):
            mime_type = file_input.mimeType
        else:
            mime_type = magic.Magic(mime=True).from_buffer(file_input.read(2048))
            file_input.name = "IO_buffer"
            file_input.seek(0)

        if mime_type.startswith("text/"):
            if mime_type not in {"text/html", "text/xml", "text/plain"}:
                print(f"📄 File recognized as text type: {mime_type}, treated as text/plain")
                mime_type = "text/plain"

        if mime_type not in estrattori:
            print(f"⚠️ MIME type not supported {mime_type} ({file_input.name}) ignored.")
            return None

        return f"{estrattori[mime_type](file_input)}"
    except Exception as e:
        print(f"❌ Error while reading: {e}")
        return None


@xtxt.register
def _(file_input: bytes) -> Optional[str]:
    """Extract text from bytes (e.g. web download content)."""
    try:
        buffer = io.BytesIO(file_input)
        buffer.name = "bytes_input"
        buffer.mimeType = magic.Magic(mime=True).from_buffer(file_input[:2048])
        return xtxt(buffer)
    except Exception as e:
        print(f"❌ Error processing bytes: {e}")
        return None


# Optional support for requests.Response
try:
    import requests

    @xtxt.register
    def _(file_input: requests.Response) -> Optional[str]:
        """Extract text from a requests.Response object."""
        try:
            return xtxt(file_input.content)
        except Exception as e:
            print(f"❌ Error processing Response: {e}")
            return None
except ImportError:
    # requests not installed, skip registration
    pass


def xtxt_from_url(url: str, **kwargs) -> Optional[str]:
    """Download content from URL and extract text."""
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


def extxt_available_formats(pretty: bool = False):
    if pretty:
        from .estrattori import pretty_names

        return sorted({pretty_names.get(mime, mime) for mime in estrattori.keys()})
    return sorted(estrattori.keys())
