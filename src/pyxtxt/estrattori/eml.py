from . import register_extractor

try:
    import email
    from email import policy
    from bs4 import BeautifulSoup
except ImportError:
    email = None

if email:
    def _html_to_text(html):
        return BeautifulSoup(html, "html.parser").get_text(separator="\n")

    def xtxt_eml(file_buffer):
        content = file_buffer.read()
        if isinstance(content, bytes):
            msg = email.message_from_bytes(content, policy=policy.default)
        else:
            msg = email.message_from_string(content, policy=policy.default)

        plain_parts = []
        html_parts = []
        for part in msg.walk():
            if part.is_multipart() or part.get_content_disposition() == "attachment":
                continue
            content_type = part.get_content_type()
            if content_type == "text/plain":
                plain_parts.append(part.get_content())
            elif content_type == "text/html":
                html_parts.append(_html_to_text(part.get_content()))
            elif not msg.is_multipart() and part.get_content_maintype() == "text":
                # Single-part message with another text type
                plain_parts.append(part.get_content())

        # The HTML version usually repeats the plain-text one (multipart/alternative):
        # use it only when there is no plain text
        parts = plain_parts or html_parts
        return "\n\n".join(part.strip() for part in parts if part and part.strip())

    register_extractor(
        "message/rfc822",
        xtxt_eml,
        name="EML"
    )
