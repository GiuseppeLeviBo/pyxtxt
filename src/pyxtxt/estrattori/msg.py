from . import register_extractor

try:
    import extract_msg
    from bs4 import BeautifulSoup
except ImportError:
    extract_msg = None

if extract_msg:
    def xtxt_msg(file_buffer):
        # extract_msg accetta direttamente i bytes del file .msg
        content = file_buffer.read()

        with extract_msg.openMsg(content) as msg:
            body = getattr(msg, "body", None)
            if body and body.strip():
                return body.strip()

            # Nessun corpo in testo semplice: usa la versione HTML
            html_body = getattr(msg, "htmlBody", None)
            if html_body:
                soup = BeautifulSoup(html_body, "html.parser")
                return soup.get_text(separator="\n").strip()

            return ""

    register_extractor(
        "application/vnd.ms-outlook",
        xtxt_msg,
        name="MSG"
    )
