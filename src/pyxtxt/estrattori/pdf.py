from . import register_extractor

def xtxt_pdf(file_input):
    return "Testo estratto da PDF"  # Qui ci andrà la vera estrazione

register_extractor(
    "application/pdf",
    xtxt_pdf,
    name="PDF"
)
