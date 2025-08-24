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

    register_extractor(
        "application/rtf",
        xtxt_rtf,
        name="RTF"
    )
