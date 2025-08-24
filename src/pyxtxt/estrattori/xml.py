from . import register_extractor
try:
    from lxml import etree
except ImportError:
    etree = None

if etree:
 def xtxt_xml(file_buffer) -> str:
    try:
        file_buffer.seek(0)
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(file_buffer, parser)
        root = tree.getroot()

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

        testo = get_text_recursively(root)
        return testo.strip()

    except Exception as e:
        print(f"⚠️ Error while extracting XML : {e}")
        return ""
 register_extractor(
    "application/xml",
    xtxt_xml,
    name="XML"
)
 register_extractor(
    "text/xml",
    xtxt_xml,
    name="XML"
)