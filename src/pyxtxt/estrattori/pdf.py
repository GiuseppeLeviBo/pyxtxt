from . import register_extractor
try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

if fitz:
 def xtxt_pdf(file_buffer):
    try:
        raw_data = file_buffer.read()
        if not raw_data:
            print("⚠️  PDF blank or not read correctly")
            return None

        doc = fitz.open(stream=raw_data, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)

    except fitz.EmptyFileError:
        print("⚠️ Error: PDF is blank or unreadable")
        return None
    except Exception as e:
        print(f"⚠️  Error during PDF extraction: {e}")
        return None




 register_extractor(
    "application/pdf",
    xtxt_pdf,
    name="PDF"
)
