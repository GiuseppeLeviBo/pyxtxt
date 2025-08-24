from . import register_extractor

try:
    import markdown
    from bs4 import BeautifulSoup
except ImportError:
    markdown = None

if markdown:
    def xtxt_md(file_buffer):
        # Legge il file come testo
        content = file_buffer.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8", errors="ignore")

        # Converte Markdown in HTML
        html = markdown.markdown(content)

        # Estrae il testo dall'HTML
        soup = BeautifulSoup(html, "html.parser")
        return soup.get_text(separator="\n")

    register_extractor(
        "text/markdown",
        xtxt_md,
        name="Markdown"
    )
