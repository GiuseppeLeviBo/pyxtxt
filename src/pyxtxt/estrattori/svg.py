from . import register_extractor
try:
    from lxml import etree
except ImportError:
    etree = None

if etree:
 def xtxt_svg(file_buffer):
     try:
         tree = etree.parse(file_buffer)
         root = tree.getroot()

        # Estrai tutto il testo dai tag <text>
         texts = [element.text for element in root.findall('.//{http://www.w3.org/2000/svg}text')]
         return "\n".join(texts)
     except Exception as e:
         print(f"⚠️ Error while extracting SVG: {e}")
         return ""
 register_extractor(
     "image/svg+xml",
     xtxt_svg,
     name="SVG"
 )
