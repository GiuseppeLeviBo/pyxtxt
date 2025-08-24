from . import register_extractor
import tempfile

try:
    import extract_msg
    from bs4 import BeautifulSoup
except ImportError:
    extract_msg = None

if extract_msg:
    def xtxt_msg(file_buffer):
        # Salva su file temporaneo perché extract_msg lavora su path
        content = file_buffer.read()
        
        with tempfile.NamedTemporaryFile(suffix=".msg", delete=False) as tmp:
            tmp.write(content)
            tmp.flush()
            
            try:
                msg = extract_msg.Message(tmp.name)
                msg.extract()  # Decodifica i contenuti
                
                parts = []
                
                if msg.body:
                    parts.append(msg.body)
                
                if msg.htmlBody:
                    soup = BeautifulSoup(msg.htmlBody, "html.parser")
                    parts.append(soup.get_text(separator="\n"))
                
                return "\n\n".join(part.strip() for part in parts if part)
            finally:
                import os
                os.unlink(tmp.name)

    register_extractor(
        "application/vnd.ms-outlook",
        xtxt_msg,
        name="MSG"
    )
