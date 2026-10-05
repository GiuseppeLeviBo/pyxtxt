from . import register_extractor
try:
    from lxml import etree
except ImportError:
    etree = None

if etree:
    def xtxt_xml(file_buffer) -> str:
        file_buffer.seek(0)
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_buffer, parser)
        root = tree.getroot()
        if root is None:
            raise ValueError("No XML content could be parsed")

        # Estrai il testo ricorsivamente da tutti i nodi
        def get_text_recursively(elem):
            texts = []
            if elem.text:
                texts.append(elem.text.strip())
            for child in elem:
                texts.append(get_text_recursively(child))
                if child.tail:
                    texts.append(child.tail.strip())
            return " ".join(filter(None, texts))

        return get_text_recursively(root).strip()

    for mime_type in ("application/xml", "text/xml"):
        register_extractor(mime_type, xtxt_xml, name="XML")
