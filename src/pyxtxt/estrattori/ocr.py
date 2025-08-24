# pyxtxt/extractors/image_ocr.py
from . import register_extractor
from io import BytesIO

try:
    import easyocr
    from PIL import Image
except ImportError:
    easyocr = None
    Image = None

if easyocr and Image:
    # Inizializza il reader OCR una volta sola
    _ocr_reader = None
    
    def _get_ocr_reader():
        global _ocr_reader
        if _ocr_reader is None:
            _ocr_reader = easyocr.Reader(['it', 'en'], gpu=False)
        return _ocr_reader
    
    def xtxt_image_ocr(file_buffer):
        try:
            # Converti il buffer in immagine PIL
            image = Image.open(BytesIO(file_buffer.read()))
            
            # Converti in RGB se necessario
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            reader = _get_ocr_reader()
            results = reader.readtext(image)
            
            # Estrai solo il testo, ordinato per posizione verticale
            texts = []
            for (bbox, text, confidence) in results:
                if confidence > 0.3:  # Filtra testo con bassa confidenza
                    texts.append(text)
            
            return "\n".join(texts)
            
        except Exception as e:
            print(f"⚠️ Error while extracting text from image: {e}")
            return ""
    
    # Registra per i formati immagine più comuni
    register_extractor("image/jpeg", xtxt_image_ocr, name="OCR")
    register_extractor("image/jpg", xtxt_image_ocr, name="OCR")
    register_extractor("image/png", xtxt_image_ocr, name="OCR")
    register_extractor("image/bmp", xtxt_image_ocr, name="OCR")
    register_extractor("image/tiff", xtxt_image_ocr, name="OCR")
    register_extractor("image/webp", xtxt_image_ocr, name="OCR")
