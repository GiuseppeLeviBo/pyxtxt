from functools import singledispatch
import io
import os
from typing import Optional

import magic

from .estrattori import estrattori

# libmagic reports some text formats (e.g. Markdown) as plain text: the file
# extension, when known, refines the detection.
_TEXT_EXTENSION_HINTS = {
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".tex": "text/x-tex",
    ".rtf": "text/rtf",
}


def _detect_mime_type(data: bytes) -> str:
    """Detect the MIME type of in-memory data.

    The whole buffer is passed to libmagic: the first few KB are not always
    enough to tell apart ZIP-based formats (e.g. XLSX is seen as application/zip).
    """
    return magic.from_buffer(data, mime=True)


def _resolve_mime_type(mime_type: str, name: Optional[str]) -> str:
    """Refine the detected MIME type and map unknown text types to text/plain."""
    if mime_type == "text/plain" and name:
        extension = os.path.splitext(name)[1].lower()
        hinted = _TEXT_EXTENSION_HINTS.get(extension)
        if hinted in estrattori:
            mime_type = hinted

    if mime_type.startswith("text/") and mime_type not in estrattori:
        print(f"📄 File recognized as text type: {mime_type}, treated as text/plain")
        mime_type = "text/plain"

    return mime_type


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
        buffer.mimeType = magic.from_file(file_input, mime=True)
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
            mime_type = _detect_mime_type(file_input.getvalue())
            file_input.seek(0)
        if not getattr(file_input, "name", None):
            file_input.name = "IO_buffer"

        mime_type = _resolve_mime_type(mime_type, file_input.name)

        if mime_type not in estrattori:
            print(f"⚠️ MIME type not supported {mime_type} ({file_input.name}) ignored.")
            return None

        return estrattori[mime_type](file_input)
    except Exception as e:
        print(f"❌ Error while reading: {e}")
        return None


@xtxt.register
def _(file_input: bytes) -> Optional[str]:
    """Extract text from bytes (e.g. web download content)."""
    try:
        buffer = io.BytesIO(file_input)
        buffer.name = "bytes_input"
        buffer.mimeType = _detect_mime_type(file_input)
        return xtxt(buffer)
    except Exception as e:
        print(f"❌ Error processing bytes: {e}")
        return None


@xtxt.register
def _(file_input: io.IOBase) -> Optional[str]:
    """Extract text from a binary file object, e.g. one returned by open(path, "rb")."""
    try:
        data = file_input.read()
        if isinstance(data, str):
            print("⚠️ File object opened in text mode: open it in binary mode ('rb')")
            return None
        buffer = io.BytesIO(data)
        name = getattr(file_input, "name", None)
        buffer.name = name if isinstance(name, str) else "file_object"
        buffer.mimeType = _detect_mime_type(data)
        return xtxt(buffer)
    except Exception as e:
        print(f"❌ Error processing file object: {e}")
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
