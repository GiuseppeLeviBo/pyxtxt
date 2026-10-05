from . import register_extractor
import io
import zipfile
try:
    from docx import Document
    from docx.oxml.ns import qn
    from docx.table import Table
    from docx.text.paragraph import Paragraph
except ImportError:
    Document = None

if Document:
    def _block_lines(parent, element):
        """Yield the text of paragraphs and tables in document order."""
        for child in element.iterchildren():
            if child.tag == qn("w:p"):
                yield Paragraph(child, parent).text
            elif child.tag == qn("w:tbl"):
                yield from _table_lines(Table(child, parent))

    def _table_lines(table):
        """Yield one line per table row, cells separated by ' | '."""
        for row in table.rows:
            seen = []
            cells = []
            for cell in row.cells:
                # Merged cells are returned once per grid column: keep the first one
                if any(cell._tc is tc for tc in seen):
                    continue
                seen.append(cell._tc)
                cell_text = " ".join(line for line in _block_lines(cell, cell._tc) if line)
                cells.append(cell_text.strip())
            if any(cells):
                yield " | ".join(cells)

    def _header_footer_lines(doc, attribute_names):
        lines = []
        for section in doc.sections:
            for attribute in attribute_names:
                part = getattr(section, attribute, None)
                if part is None or part.is_linked_to_previous:
                    continue
                for line in _block_lines(part, part._element):
                    if line and line not in lines:
                        lines.append(line)
        return lines

    def xtxt_docx(file_buffer) -> str:
        try:
            # Copia del buffer per poterlo riutilizzare
            file_buffer.seek(0)
            data = file_buffer.read()
            buffer_copy = io.BytesIO(data)

            if not zipfile.is_zipfile(buffer_copy):
                print("⚠️ Invalid DOCX (not a ZIP file)")
                return ""

            buffer_copy.seek(0)
            doc = Document(buffer_copy)

            headers = _header_footer_lines(doc, ("first_page_header", "header", "even_page_header"))
            body = list(_block_lines(doc, doc.element.body))
            footers = _header_footer_lines(doc, ("first_page_footer", "footer", "even_page_footer"))
            return "\n".join(headers + body + footers)

        except Exception as e:
            print(f"⚠️  Error during extraction DOCX: {e}")
            return ""

    register_extractor(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        xtxt_docx,
        name="DOCX"
    )
