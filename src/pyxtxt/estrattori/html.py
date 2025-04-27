from . import register_extractor
from bs4 import BeautifulSoup
def xtxt_html(file_buffer):
    soup = BeautifulSoup(file_buffer.read(), "html.parser")
    return soup.get_text(separator="\n")
register_extractor(
    "text/html",
    xtxt_html,
    name="HTML"
)
