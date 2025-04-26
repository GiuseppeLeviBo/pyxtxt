from . import register_extractor

def xtxt_docx(file_input):
    return "Testo estratto da DOCX"  # Qui ci andrà la vera estrazione

register_extractor(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    xtxt_docx,
    name="DOCX"
)
