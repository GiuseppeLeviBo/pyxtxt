from . import register_extractor
try:
    from lxml import etree
except ImportError:
    etree = None

if etree:
    _SVG_TEXT_TAGS = ("{http://www.w3.org/2000/svg}text", "text")

    def xtxt_svg(file_buffer):
        try:
            parser = etree.XMLParser(recover=True, resolve_entities=False, no_network=True)
            tree = etree.parse(file_buffer, parser)

            # Testo dei tag <text>, compresi i <tspan> annidati
            texts = []
            for element in tree.getroot().iter(*_SVG_TEXT_TAGS):
                text = "".join(element.itertext(tag=etree.Element)).strip()
                if text:
                    texts.append(text)
            return "\n".join(texts)
        except Exception as e:
            print(f"⚠️ Error while extracting SVG: {e}")
            return ""

    register_extractor(
        "image/svg+xml",
        xtxt_svg,
        name="SVG"
    )
