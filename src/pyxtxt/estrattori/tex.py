from . import register_extractor

try:
    from pylatexenc.latex2text import LatexNodes2Text
except ImportError:
    LatexNodes2Text = None

if LatexNodes2Text:
    def xtxt_tex(file_buffer):
        content = file_buffer.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")

        text = LatexNodes2Text().latex_to_text(content)
        return text.strip()

    # libmagic reports LaTeX sources as text/x-tex
    for mime_type in ("application/x-tex", "text/x-tex"):
        register_extractor(mime_type, xtxt_tex, name="LaTeX")
