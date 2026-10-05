from . import register_extractor

try:
    from striprtf.striprtf import rtf_to_text
except ImportError:
    rtf_to_text = None

if rtf_to_text:
    def xtxt_rtf(file_buffer):
        content = file_buffer.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")

        return rtf_to_text(content)

    # libmagic reports RTF as text/rtf
    for mime_type in ("application/rtf", "text/rtf"):
        register_extractor(mime_type, xtxt_rtf, name="RTF")
