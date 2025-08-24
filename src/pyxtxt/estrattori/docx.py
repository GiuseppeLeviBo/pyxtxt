from . import register_extractor
import io
import zipfile
try:
    from docx import Document
except ImportError:
    Document = None

if Document:
 def xtxt_docx(file_buffer) -> str:
    try:
        # Copia del buffer per poterlo riutilizzare
        file_buffer.seek(0)
        data = file_buffer.read()
        buffer_copy = io.BytesIO(data)

        if not zipfile.is_zipfile(buffer_copy):
            print("⚠️ Invalid DOCX (not a ZIP file)")
            return ""

        buffer_copy.seek(0)
        doc = Document(buffer_copy)

        text = "\n".join(p.text for p in doc.paragraphs)
        return text

    except Exception as e:
        print(f"⚠️  Error during extraction DOCX: {e}")
        return ""

 register_extractor(
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    xtxt_docx,
    name="DOCX"
)
