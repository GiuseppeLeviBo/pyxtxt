from . import register_extractor
try:
    from lxml import etree
except ImportError:
    etree = None

if etree:
    _SVG_TEXT_TAGS = ("{http://www.w3.org/2000/svg}text", "text")

    def xtxt_svg(file_buffer):
        parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True)
        root = etree.parse(file_buffer, parser).getroot()
        if root is None:
            raise ValueError("No SVG content could be parsed")

        # Testo dei tag <text>, compresi i <tspan> annidati
        texts = []
        for element in root.iter(*_SVG_TEXT_TAGS):
            text = "".join(element.itertext(tag=etree.Element)).strip()
            if text:
                texts.append(text)
        return "\n".join(texts)

    register_extractor(
        "image/svg+xml",
        xtxt_svg,
        name="SVG"
    )
