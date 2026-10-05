from . import register_extractor
try:
    from odf import teletype
    from odf.namespaces import TEXTNS
    from odf.opendocument import load
except ImportError:
    load = None

if load:
    # Paragraphs and headings; list items and table cells contain paragraphs too
    _TEXT_BLOCKS = {(TEXTNS, "p"), (TEXTNS, "h")}

    def _block_texts(node):
        """Yield the text of paragraphs and headings in document order."""
        for child in node.childNodes:
            if getattr(child, "qname", None) in _TEXT_BLOCKS:
                # extractText includes nested spans, links, tabs and line breaks
                yield teletype.extractText(child)
            elif child.nodeType == child.ELEMENT_NODE:
                yield from _block_texts(child)

    def xtxt_odt(file_buffer):
        odt_doc = load(file_buffer)
        return "\n".join(text for text in _block_texts(odt_doc.text) if text.strip())

    register_extractor(
        "application/vnd.oasis.opendocument.text",
        xtxt_odt,
        name="ODT"
    )
