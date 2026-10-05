from . import register_extractor
try:
    import pymupdf as fitz  # PyMuPDF >= 1.24.3
except ImportError:
    try:
        import fitz  # older PyMuPDF; the `fitz` name is deprecated
    except ImportError:
        fitz = None

if fitz:
    def xtxt_pdf(file_buffer):
        raw_data = file_buffer.read()
        if not raw_data:
            raise ValueError("PDF is empty")

        doc = fitz.open(stream=raw_data, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)

    register_extractor(
        "application/pdf",
        xtxt_pdf,
        name="PDF"
    )
