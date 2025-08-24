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

    register_extractor(
        "application/x-tex",
        xtxt_tex,
        name="LaTeX"
    )
