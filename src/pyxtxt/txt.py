from . import register_extractor
def xtxt_txt(file_buffer):
    return file_buffer.read().decode("utf-8", errors="ignore")
register_extractor(
     "text/plain",
     xtxt_txt,
    name="TXT"
)