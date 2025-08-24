from . import register_extractor
try:
    from odf.opendocument import load
    from odf.text import P
except ImportError:
    load = None

if load:
 def xtxt_odt(file_buffer):
    odt_doc = load(file_buffer)
    paragraphs = odt_doc.getElementsByType(P)
    
    testo = []
    for p in paragraphs:
        contenuto = []
        for n in p.childNodes:
            if n.nodeType == 3:  # TEXT_NODE
                contenuto.append(n.data)
        if contenuto:
            testo.append("".join(contenuto))
    
    return "\n".join(testo)
 register_extractor(
     "application/vnd.oasis.opendocument.text",
     xtxt_odt,
    name="ODT"
)
