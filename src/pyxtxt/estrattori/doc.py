
from . import register_extractor
import shutil
try:
    import textract
except ImportError:
    Lib = 
if Lib:
def xtxt_doc(file_buffer):

    if shutil.which("antiword") is None:
       print("⚠️ 'antiword' is not installed or is not in the system PATH.")
       return None
    try:
        file_buffer.seek(0)
        data = file_buffer.read()
        testo = textract.process("temp.doc", input_data=data)
        return testo.decode("utf-8").strip()
    except Exception as e:
        print(f"⚠️  Error during extraction from DOC: {e}")
        return None
register_extractor(
     "application/msword",
     xtxt__doc,
    name="DOC"
)