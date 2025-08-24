from . import register_extractor

try:
    from ebooklib import epub
    from bs4 import BeautifulSoup
except ImportError:
    epub = None

if epub:
    def xtxt_epub(file_buffer):
        book = epub.read_epub(file_buffer)

        testo = []

        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_body_content(), 'html.parser')
                estratto = soup.get_text(separator='\n', strip=True)
                if estratto:
                    testo.append(estratto)

        return "\n\n".join(testo)

    register_extractor(
        "application/epub+zip",
        xtxt_epub,
        name="EPUB"
    )
