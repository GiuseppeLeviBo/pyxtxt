from . import register_extractor

try:
    import email
    from email import policy
    from bs4 import BeautifulSoup
except ImportError:
    email = None

if email:
    def xtxt_eml(file_buffer):
        content = file_buffer.read()
        if isinstance(content, bytes):
            msg = email.message_from_bytes(content, policy=policy.default)
        else:
            msg = email.message_from_string(content, policy=policy.default)

        parts = []

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    parts.append(part.get_content())
                elif content_type == "text/html":
                    html = part.get_content()
                    soup = BeautifulSoup(html, "html.parser")
                    parts.append(soup.get_text(separator="\n"))
        else:
            content_type = msg.get_content_type()
            payload = msg.get_content()
            if content_type == "text/html":
                soup = BeautifulSoup(payload, "html.parser")
                parts.append(soup.get_text(separator="\n"))
            else:
                parts.append(payload)

        return "\n\n".join(part.strip() for part in parts if part)

    register_extractor(
        "message/rfc822",
        xtxt_eml,
        name="EML"
    )
