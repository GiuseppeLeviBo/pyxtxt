from functools import singledispatch
import io
import logging
import os
from typing import Optional

import magic

from .estrattori import estrattori

logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Text could not be extracted: unreadable or corrupted file, extractor failure, ..."""


class UnsupportedFormatError(ExtractionError):
    """The file type is not supported, or the library needed to read it is not installed."""


# libmagic reports some text formats (e.g. Markdown) as plain text: the file
# extension, when known, refines the detection.
_TEXT_EXTENSION_HINTS = {
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".tex": "text/x-tex",
    ".rtf": "text/rtf",
    ".eml": "message/rfc822",  # emails not starting with Received:/From:/Return-Path: ...
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
        logger.info(f"File recognized as text type: {mime_type}, treated as text/plain")
        mime_type = "text/plain"

    return mime_type


def _fail(message: str, raise_errors: bool, cause: Optional[BaseException] = None,
          error_class: type = ExtractionError) -> None:
    """Report a failure: raise when raise_errors is set, otherwise log it and return None."""
    if raise_errors:
        raise error_class(message) from cause
    logger.warning(message)
    return None


def _extract(buffer: io.BytesIO, mime_type: str, raise_errors: bool) -> Optional[str]:
    """Run the extractor registered for the MIME type on a buffer positioned at 0."""
    mime_type = _resolve_mime_type(mime_type, buffer.name)

    if mime_type not in estrattori:
        return _fail(f"MIME type not supported {mime_type} ({buffer.name}) ignored.",
                     raise_errors, error_class=UnsupportedFormatError)

    try:
        return estrattori[mime_type](buffer)
    except Exception as e:
        return _fail(f"Error while extracting text from {buffer.name} ({mime_type}): {e}", raise_errors, e)


@singledispatch
def xtxt(file_input, raise_errors: bool = False):
    """Extract text from a file path, binary file object, BytesIO buffer, bytes or requests.Response.

    Returns the extracted text ("" when the file contains no text), or None when the
    text cannot be extracted. With raise_errors=True a failure raises ExtractionError
    (UnsupportedFormatError for unsupported file types) instead of returning None.
    """
    raise NotImplementedError(f"Type not supported : {type(file_input)}")


@xtxt.register
def _(file_input: str, raise_errors: bool = False) -> Optional[str]:
    """Extract text from a file path."""
    try:
        with open(file_input, "rb") as f:
            data = f.read()
        mime_type = magic.from_file(file_input, mime=True)
    except Exception as e:
        return _fail(f"File opening error '{file_input}': {e}", raise_errors, e)

    buffer = io.BytesIO(data)
    buffer.name = file_input
    return _extract(buffer, mime_type, raise_errors)


@xtxt.register
def _(file_input: io.BytesIO, raise_errors: bool = False) -> Optional[str]:
    """Extract text from a BytesIO buffer."""
    if not getattr(file_input, "name", None):
        file_input.name = "IO_buffer"
    try:
        mime_type = getattr(file_input, "mimeType", None) or _detect_mime_type(file_input.getvalue())
    except Exception as e:
        return _fail(f"File type detection failed ({file_input.name}): {e}", raise_errors, e)

    file_input.seek(0)
    return _extract(file_input, mime_type, raise_errors)


@xtxt.register
def _(file_input: bytes, raise_errors: bool = False) -> Optional[str]:
    """Extract text from bytes (e.g. web download content)."""
    buffer = io.BytesIO(file_input)
    buffer.name = "bytes_input"
    return xtxt(buffer, raise_errors=raise_errors)


@xtxt.register
def _(file_input: io.IOBase, raise_errors: bool = False) -> Optional[str]:
    """Extract text from a binary file object, e.g. one returned by open(path, "rb")."""
    try:
        data = file_input.read()
    except Exception as e:
        return _fail(f"Error reading file object: {e}", raise_errors, e)

    if isinstance(data, str):
        return _fail("File object opened in text mode: open it in binary mode ('rb')", raise_errors)

    buffer = io.BytesIO(data)
    name = getattr(file_input, "name", None)
    buffer.name = name if isinstance(name, str) else "file_object"
    return xtxt(buffer, raise_errors=raise_errors)


# Optional support for requests.Response
try:
    import requests

    @xtxt.register
    def _(file_input: requests.Response, raise_errors: bool = False) -> Optional[str]:
        """Extract text from a requests.Response object."""
        return xtxt(file_input.content, raise_errors=raise_errors)
except ImportError:
    # requests not installed, skip registration
    pass


def xtxt_from_url(url: str, *, raise_errors: bool = False, **kwargs) -> Optional[str]:
    """Download content from URL and extract text.

    Extra keyword arguments are passed to requests.get().
    """
    try:
        import requests
    except ImportError as e:
        return _fail("requests library not installed. Install with: pip install requests", raise_errors, e)

    try:
        response = requests.get(url, **kwargs)
        response.raise_for_status()
    except Exception as e:
        return _fail(f"Error downloading from URL {url}: {e}", raise_errors, e)

    return xtxt(response.content, raise_errors=raise_errors)


def xtxt_available_formats(pretty: bool = False):
    """List the supported MIME types, or their short names with pretty=True."""
    if pretty:
        from .estrattori import pretty_names

        return sorted({pretty_names.get(mime, mime) for mime in estrattori.keys()})
    return sorted(estrattori.keys())


# Former name, kept for backward compatibility
extxt_available_formats = xtxt_available_formats
